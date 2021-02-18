import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol

logging.basicConfig(filename='server.log', level=logging.INFO)

class Server:
    
    def __init__(self, loop, speed, distance, rpm): 
        self._speed = speed
        self._distance = distance
        self._rpm = rpm
        self._loop = loop
        self._clients = set()

        self._speed.register_observer(self.send_speed)
        self._distance.register_observer(self.send_distance)
        self._rpm.register_observer(self.send_rpm)

    def byteArrayToString(self, byteArray):
        str_value = '"'
        for byte in byteArray:
            if str_value != '"':
                str_value += ','
            str_value += hex(byte)
        str_value += '"'
        return str_value

    
    def send_speed(self, value) -> None:
        str_value = self.byteArrayToString(value)
        coro = self.send_to_clients("{ %sspeed%s: %s }"%('"','"', str_value))
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def send_distance(self, value) -> None:
        str_value = self.byteArrayToString(value)
        coro = self.send_to_clients("{ %sdistance%s: %s }"%('"','"', str_value))
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def send_rpm(self, value) -> None:
        str_value = self.byteArrayToString(value)
        coro = self.send_to_clients("{ %srpm%s: %s }"%('"','"', str_value))
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self._clients.add(ws)
        logging.info("%s connects."%(str(ws.remote_address)))

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self._clients.remove(ws)
        logging.info("%s disconnects."%(str(ws.remote_address)))

    async def send_to_clients(self, message: str) -> None:
        if self._clients:
            await asyncio.wait([client.send(message) for client in self._clients])
    
    async def distribute(self, ws: WebSocketServerProtocol) -> None: 
        async for message in ws:
            await self.send_to_clients(message)

    async def ws_handler(self, ws: WebSocketServerProtocol, url: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)