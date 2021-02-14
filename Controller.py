from Devices.CAN_Devices import CAN_devices, Default_CAN_device, CAN_device, CAN_speed, CAN_rpm, CAN_distance
from Devices.Devices import Devices

import API.API as API
import websockets
import asyncio

from Data.ValueObserver import ValueObserver

import time

import threading

def run_server(start_server, loop):
    loop.run_until_complete(start_server)
    loop.run_forever()

speed = ValueObserver(0)
rpm = ValueObserver(0)
distance = ValueObserver(0)

loop = asyncio.get_event_loop()
server = API.Server(loop, speed, distance, rpm)
start_server = websockets.serve(server.ws_handler, 'localhost', 4000)
thread = threading.Thread(target=run_server, args=(start_server, loop))
thread.start()

while(1):
    time.sleep(1)
    speed.value += 1