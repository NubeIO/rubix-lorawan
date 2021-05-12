from .model_point import PointModel
from src.interfaces.device import DeviceModels


ELSYS_ERS_CO2_POINTS = [
    {'name': 'humidity', 'cov_threshold': 1},
    {'name': 'light', 'cov_threshold': 1},
    {'name': 'motion', 'cov_threshold': 1},
    {'name': 'temperature', 'cov_threshold': 1},
    {'name': 'voltage', 'cov_threshold': 1},
    {'name': 'rssi', 'cov_threshold': 0.5},
]

ELSYS_ERS_VOC_POINTS = [
    {'name': 'humidity', 'cov_threshold': 1},
    {'name': 'light', 'cov_threshold': 1},
    {'name': 'motion', 'cov_threshold': 1},
    {'name': 'temperature', 'cov_threshold': 1},
    {'name': 'voltage', 'cov_threshold': 1},
    {'name': 'rssi', 'cov_threshold': 0.5},
]


ELSYS_ERS_SOUND_POINTS = [
    {'name': 'voltage', 'cov_threshold': 1},
    {'name': 'rssi', 'cov_threshold': 0.5},
]


ELSYS_EMS_DOOR_POINTS = [
    {'name': 'voltage', 'cov_threshold': 1},
    {'name': 'rssi', 'cov_threshold': 0.5},
]


def get_device_points(model: DeviceModels):
    if model is DeviceModels.ELSYS_ERS_CO2:
        points_json = ELSYS_ERS_CO2_POINTS
    elif model is DeviceModels.ELSYS_ERS_VOC:
        points_json = ELSYS_ERS_VOC_POINTS
    elif model is DeviceModels.ELSYS_ERS_SOUND:
        points_json = ELSYS_ERS_SOUND_POINTS
    elif model is DeviceModels.ELSYS_EMS_DOOR:
        points_json = ELSYS_EMS_DOOR_POINTS
    else:
        raise Exception('Invalid DeviceModel')
    point_models = []
    for data in points_json:
        point_models.append(PointModel(**data))
    return point_models
