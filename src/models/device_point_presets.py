from .model_point import PointModel
from src.interfaces.device import DeviceModels

# NOTE: names must match decoder payload names/keys


ELSYS_ERS_CO2_POINTS = [
    {'name': 'voltage',
     'cov_threshold': 0.01},
    {'name': 'rssi',
     'cov_threshold': 1},
    {'name': 'pulses',
     'cov_threshold': 1}
]

ELSYS_ERS_VOC_POINTS = [
    {'name': 'voltage',
     'cov_threshold': 0.01},
    {'name': 'rssi',
     'cov_threshold': 1},
    {'name': 'pulses',
     'cov_threshold': 1}
]


def get_device_points(model: DeviceModels):
    if model is DeviceModels.ELSYS_ERS_CO2:
        points_json = ELSYS_ERS_CO2_POINTS
    elif model is DeviceModels.ELSYS_ERS_VOC:
        points_json = ELSYS_ERS_VOC_POINTS
    else:
        raise Exception('Invalid DeviceModel')
    point_models = []
    for data in points_json:
        point_models.append(PointModel(**data))
    return point_models
