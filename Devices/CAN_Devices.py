import can
from .Devices import Device, Devices

class CAN_devices(Devices):
    
    def read(self):
        pass

    def write(self, data):
        pass


class Default_CAN_device(CAN_devices):

    def __init__(self, interface, bitRate=None):
        self._interface = interface
        self._bitRate = bitRate 
        if self._bitRate != None:
            
            self._bus = can.interface.Bus(bustype='socketcan', channel=self._interface, bitrate=bitRate)
        else:
            self._bus = can.interface.Bus(bustype='socketcan', channel=self._interface)

    def interprete_data_frame(self, data_frame):
        return 'not_captured_device', data_frame['data']

    @property
    def bus(self):
        return self._bus


class CAN_device(CAN_devices):
    _id = None
    _can_devices = None

    def __init__(self, can_devices, id, variable):
        self._can_devices = can_devices
        self._id = id
        self._variable = variable 

    @property
    def can_devices(self):
        return self._can_devices
    
    def id(self):
        return self._id

    def get_data(self, data_frame):
        pass
    
    def read_bus(self):
        message = self.bus.recv()

        data_frame = {
            'timestamp': message.timestamp,
            'id': hex(message.arbitration_id),
            'data': message.data,
            'dlc': message.dlc
        }

        return data_frame

    def interprete_data_frame(self, data_frame):
        if data_frame['id'] == self.id():
            return self.get_data(data_frame)
        else:
            self.can_devices.interprete_data_frame(data_frame)

    def write(self, data):
        self.bus.Message(arbitration_id=self._id, data=data['data'], is_extended_id=data['isExtended'])

    def read(self):
        data_frame = self.read_bus()
        return self.interprete_data_frame(data_frame)

    @property
    def bus(self):
        return self.can_devices.bus


class CAN_speed(CAN_device):
    def __init__(self, can_devices, id, variable, max_speed):
        super().__init__(can_devices, id, variable)
        self._max_speed = max_speed

    def get_data(self, data_frame):
        value = data_frame['data'][0]
        value = value * self._max_speed / 256
        if value != self._variable.value:
            self._variable.value = value
        return 'speed', value

    def write(self, data):
        processed_data = {
            'data': data,
            'isExtended': False
        }
        super.write(processed_data)
        pass


class CAN_rpm(CAN_device):
    def __init__(self, can_devices, id, variable, max_rpm):
        super().__init__(can_devices, id, variable)
        self._max_rpm = max_rpm

    def get_data(self, data_frame):
        value = data_frame['data'][0]
        value = value * self._max_rpm / 256
        if value != self._variable.value:
            self._variable.value = value
        return 'rpm', value

    def write(self, data):
        pass

class CAN_engine(CAN_device):
    def __init__(self, can_devices, id, speed_obs, rpm_obs, max_speed, max_rpm):
        super().__init__(can_devices, id, None)
        self._speed = speed_obs
        self._rpm = rpm_obs
        
        self._max_speed = max_speed
        self._max_rpm = max_rpm

    def get_data(self, data_frame):
        speed = data_frame['data'][0]
        speed = speed * self._max_speed / 256

        rpm = data_frame['data'][1]
        rpm = rpm * self._max_rpm / 256

        if speed != self._speed.value:
            self._speed.value = speed
        
        if rpm != self._rpm.value:
            self._rpm.value = rpm
        
        return 'speed', speed, 'rpm', rpm


class CAN_distance(CAN_device):
    def __init__(self, can_devices, id, variable, max_dist):
        super().__init__(can_devices, id, variable)
        self._max_dist = max_dist

    def get_data(self, data_frame):
        value = data_frame['data'][0]
        value = value * self._max_dist / 256
        if value != self._variable.value:
            self._variable.value = value
        return 'distance', value

    def write(self, data):
        pass
