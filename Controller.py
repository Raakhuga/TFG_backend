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

def read_can(can):
    while True: 
        can.read()

# Create observable variables
speed = ValueObserver(0)
rpm = ValueObserver(0)
distance = ValueObserver(0)

# Initiate thread with websockets api
loop = asyncio.get_event_loop()
server = API.Server(loop, speed, distance, rpm)
start_server = websockets.serve(server.ws_handler, '192.168.100.1', 4000)
thread = threading.Thread(target=run_server, args=(start_server, loop))
thread.start()

# Initiate can bus reader
can = Default_CAN_device('vcan0')
can = CAN_speed(can, hex(1), speed)
can = CAN_rpm(can, hex(2), rpm)
can = CAN_distance(can, hex(3), distance)
read_can(can)

'''
while(1):
    time.sleep(1)
    speed.value += 10
    if (speed.value == 200):
        speed.value = 0
'''