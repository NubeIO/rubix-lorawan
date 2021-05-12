from enum import Enum, auto


class DeviceTypes(Enum):
    ELSYS_ERS = auto()
    ELSYS_EMS = auto()


class DeviceModels(Enum):
    ELSYS_ERS_CO2 = auto()
    ELSYS_ERS_VOV = auto()
    ELSYS_ERS_SOUND = auto()
    ELSYS_EMS_DOOR = auto()

