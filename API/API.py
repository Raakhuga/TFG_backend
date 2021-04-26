import asyncio
import logging
import websockets
import json
from websockets import WebSocketServerProtocol

logging.basicConfig(filename='server.log', level=logging.INFO)

class Server:
    def __init__(self, loop, speed, distance, rpm, tooClose, config_dict, config_file_path): 
        #Observers
        self._speed = speed
        self._distance = distance
        self._rpm = rpm
        self._tooClose = tooClose

        self._loop = loop
        self._config_dict = config_dict
        self._config_file_path = config_file_path
        self._clients = set()

        #Observers registrations
        self._speed.register_observer(self.send_speed)
        self._distance.register_observer(self.send_distance)
        self._rpm.register_observer(self.send_rpm)
        self._tooClose.register_observer(self.send_tooClose)
    
    #Observers Callbacks
    def send_speed(self, value) -> None:
        coro = self.send_to_clients("{ \"speed\": %d }"%(value))
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def send_distance(self, value) -> None:
        coro = self.send_to_clients("{ \"distance\": %d }"%(value))
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def send_rpm(self, value) -> None:
        coro = self.send_to_clients("{ \"rpm\": %d }"%(value))
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def send_tooClose(self, value) -> None:
        dict = {
            "tooClose": value
        }
        coro = self.send_to_clients(json.dumps(dict))
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    #On new connection send car config and dashboards and add that id to our client set
    async def register(self, ws: WebSocketServerProtocol) -> None:
        self._clients.add(ws)
        await ws.send("{ \"car\": %s }"%(json.dumps(self._config_dict['car'])))
        await ws.send("{ \"dashboards\": %s }"%(json.dumps(self._config_dict['dashboards'])))
        logging.info("%s connects."%(str(ws.remote_address)))

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self._clients.remove(ws)    
        logging.info("%s disconnects."%(str(ws.remote_address)))

    async def send_to_clients(self, message: str) -> None:
        if self._clients:
            await asyncio.wait([client.send(message) for client in self._clients])
    
    #Handle messages from clients
    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        def isConfig(message):
            try :
                dict = json.loads(message)
                return 'configuration' in dict.keys()
             
            except:
                return False

        def parseConfig(message):
            dictionary = json.loads(message)
            dashboards = {
                "dashboards": dictionary['configuration']['dashboards']
            }
            car = {
                "car": {
                    "max_speed": dictionary['configuration']['maxSpeed'],
                    "max_rpm": dictionary['configuration']['maxRpm'],
                    "max_distance": self._config_dict['car']['max_distance']
                }
            }
            return dashboards, car

        def saveConfig(dashboards, car):
            self._config_dict['car'] = car['car']
            self._config_dict['dashboards'] = dashboards['dashboards']
            with open(self._config_file_path, 'w') as config_file:
                config_file.write(json.dumps(self._config_dict, indent=4))

        async for message in ws:
            if isConfig(message):
                dashboards, car = parseConfig(message)
                saveConfig(dashboards, car)
                message = json.dumps(car)
                await self.send_to_clients(json.dumps(dashboards))

            await self.send_to_clients(message)

    async def ws_handler(self, ws: WebSocketServerProtocol, url: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)
