from Devices.CAN_Devices import CAN_devices, Default_CAN_device, CAN_device, CAN_speed, CAN_rpm, CAN_engine, CAN_distance
from Devices.Devices import Devices
from Devices.Audio_device import Audio

from Data.ValueObserver import ValueObserver

import API.API as API

import websockets
import asyncio

import sys
import time
import json
import threading

def run_server(start_server, loop):
    loop.run_until_complete(start_server)
    loop.run_forever()

def read_can(can):
    while True: 
        can.read()

def hex_string_to_hex_value(hex_string):
    int_value = int(hex_string, 16)
    return hex(int_value)

def main():

    # Getting the config variables
    if len(sys.argv) == 1:
        CONFIG_FILE_PATH = 'Configurations/default.json'
    else:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print("Usage: Controller.py <config_file_path>\n <Configurations/default.json> will be used if no config_file_path is specified.")
        else:
            CONFIG_FILE_PATH = sys.argv[1]

    config_file = open(CONFIG_FILE_PATH, 'r')
    config_dict = json.load(config_file)
    config_file.close()

    # Create observable variables
    speed = ValueObserver(0)
    rpm = ValueObserver(0)
    distance = ValueObserver(0)
    tooClose = ValueObserver(False)

    # Initiate thread with websockets api
    loop = asyncio.get_event_loop()
    server = API.Server(loop, speed, distance, rpm, tooClose, config_dict, CONFIG_FILE_PATH)
    start_server = websockets.serve(server.ws_handler, config_dict['serve_ip'], config_dict['serve_port'])
    ws_thread = threading.Thread(target=run_server, args=(start_server, loop))
    ws_thread.start()

    # Initiate can bus reader
    can = Default_CAN_device(config_dict['interface'])
    can_engine = CAN_engine(can, hex_string_to_hex_value(config_dict['engine_id']), speed, rpm, config_dict['car']['max_speed'], config_dict['car']['max_rpm'])
    can_distance = CAN_distance(can_engine, hex_string_to_hex_value(config_dict['distance_id']), distance, config_dict['car']['max_distance'])
    can = can_distance
    bus_thread = threading.Thread(target=read_can, args=([can]))
    bus_thread.start()

    # Initiate Audio Device
    audio = Audio(speed, distance, tooClose)

    # Loop the main thread
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
