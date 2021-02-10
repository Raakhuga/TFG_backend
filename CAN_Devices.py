class CAN_devices:
    
    def read(self):
        pass

    def write(self, data):
        pass


class Default_CAN_device(CAN_devices):

    def __init__(self, id):
        self._id = id

    def interprete_data_frame(self, data_frame):
        return 'not_captured_device', data_frame['data']


class CAN_device(CAN_devices):
    _id = None
    _can_devices = None

    def __init__(self, can_devices, id):
        self._can_devices = can_devices
        self._id = id

    def can_devices(self):
        return self._can_devices
    
    def id(self):
        return self._id

    def get_data(self, data_frame):
        pass
    
    def read_bus(self):
        data_frame = { # bus read
            "id": None,
            "data": None
        }

        return data_frame

    def interprete_data_frame(self, data_frame):
        if data_frame['id'] == self.id():
            return self.get_data(data_frame)
        else:
            self.can_devices().interprete_data_frame()

    def read(self):
        data_frame = self.read_bus()
        return self.interprete_data_frame(data_frame)


class CAN_speed(CAN_device):
    def get_data(self, data_frame):
        return 'speed', data_frame['data']

    def write(self, data):
        pass


class CAN_rpm(CAN_device):
    def get_data(self, data_frame):
        return 'rpm', data_frame['data']

    def write(self, data):
        pass

class CAN_distance(CAN_device):
    def get_data(self, data_frame):
        return 'distance', data_frame['data']

    def write(self, data):
        pass
