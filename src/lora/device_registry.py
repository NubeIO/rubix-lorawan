from src.utils import Singleton


class DeviceRegistry(metaclass=Singleton):

    def __init__(self):
        self.__devices = {}

    def get_devices(self):
        return self.__devices

    def get_device(self, dev_eui):
        if dev_eui in self.__devices.keys():
            return self.__devices[dev_eui]
        return None

    def add_device(self, dev_eui, _uuid):
        self.__devices[dev_eui] = _uuid

    def remove_device(self, dev_eui):
        self.__devices.pop(dev_eui, None)
