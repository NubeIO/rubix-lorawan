from abc import abstractmethod

from chirpstack import device
from flask_restful import marshal_with, reqparse
from rubix_http.exceptions.exception import NotFoundException

from src.lora import ChirpStackListener
from src.models.model_device import DeviceModel
from src.resources.device.device_base import DeviceBase
from src.resources.model_fields import device_fields


class DeviceSingularBase(DeviceBase):
    parser_patch = reqparse.RequestParser()
    parser_patch.add_argument('name', type=str, store_missing=False)
    parser_patch.add_argument('enable', type=bool, store_missing=False)
    parser_patch.add_argument('dev_eui', type=str, store_missing=False)
    parser_patch.add_argument('device_type', type=str, store_missing=False)
    parser_patch.add_argument('device_model', type=str, store_missing=False)
    parser_patch.add_argument('profile_id', type=str, store_missing=False)
    parser_patch.add_argument('app_id', type=str, store_missing=False)
    parser_patch.add_argument('description', type=str, store_missing=False)

    @classmethod
    @marshal_with(device_fields)
    def get(cls, value):
        device = cls.get_device(value)
        if not device:
            raise NotFoundException('LoRa Device is not found')
        return device

    @classmethod
    def patch(cls, value):
        data = DeviceSingularBase.parser_patch.parse_args()
        dev = cls.get_device(value)
        if not dev:
            raise NotFoundException(f"Does not exist in database {value}")
        cs = ChirpStackListener().chirpstack_session()
        cs_status = ChirpStackListener().connection_status()
        description = data.get("description")
        dev_eui = data.get("dev_eui")
        name = data.get("name")
        profile_id = data.get("profile_id")
        app_id = data.get("app_id")
        if cs_status:
            d = device.Devices(chirpstack_connection=cs)
            d.description = description
            d.deveui = dev_eui
            d.name = name
            d.profile_id = profile_id
            d.appid = app_id
            res = d.update(dev_eui=dev_eui)
            if res.get("result") == "success":
                return cls.update_device(dev, data)
            elif res.get("result") == "failure":
                return res
        else:
            raise NotFoundException(f"lorawan server not running or no device: {value}")

    @classmethod
    def delete(cls, value):
        data = DeviceSingularBase.parser_patch.parse_args()
        dev_eui = data.get("dev_eui")
        dev = cls.get_device(value)
        cs = ChirpStackListener().chirpstack_session()
        cs_status = ChirpStackListener().connection_status()
        if cs_status:
            d = device.Devices(chirpstack_connection=cs)
            res = d.delete(dev_eui=dev_eui)
            if res.get("result") == "success":
                return cls.delete_device(dev)
            elif res.get("result") == "failure":
                return res
        else:
            raise NotFoundException(f"lorawan server not running or no device: {value}")

    @classmethod
    @abstractmethod
    def get_device(cls, value) -> DeviceModel:
        raise NotImplementedError('Need to implement')


class DeviceSingularByUUID(DeviceSingularBase):
    @classmethod
    def get_device(cls, value) -> DeviceModel:
        return DeviceModel.find_by_uuid(value)


class DeviceSingularByName(DeviceSingularBase):
    @classmethod
    def get_device(cls, value) -> DeviceModel:
        return DeviceModel.find_by_name(value)


class DeviceSingularByEUI(DeviceSingularBase):
    @classmethod
    def get_device(cls, value) -> DeviceModel:
        return DeviceModel.find_by_dev_eui(value)
