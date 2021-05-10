from flask_restful import reqparse
from rubix_http.exceptions.exception import NotFoundException
from rubix_http.resource import RubixResource

from src import db
from src.lora import DeviceRegistry
from src.models.model_device import DeviceModel


class DeviceBase(RubixResource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, store_missing=False)
    parser.add_argument('enable', type=bool, store_missing=False)
    parser.add_argument('dev_eui', type=str, store_missing=False)
    parser.add_argument('device_type', type=str, required=True, store_missing=False)
    parser.add_argument('device_model', type=str, store_missing=False)
    parser.add_argument('profile_id', type=str, store_missing=False)
    parser.add_argument('app_id', type=str, store_missing=False)
    parser.add_argument('description', type=str, store_missing=False)

    @classmethod
    def add_device(cls, _uuid: str, data: dict):
        device: DeviceModel = DeviceModel(uuid=_uuid, **data)
        device.save_to_db()
        DeviceRegistry().add_device(device.dev_eui, device.uuid)
        device.update_mqtt()
        return device

    @classmethod
    def update_device(cls, device: DeviceModel, data: dict):
        original_dev_eui = device.dev_eui
        device: DeviceModel = DeviceModel.find_by_uuid(device.uuid)
        device.update(**data)
        if original_dev_eui != device.dev_eui:
            DeviceRegistry().remove_device(original_dev_eui)
        db.session.commit()
        DeviceRegistry().add_device(device.dev_eui, device.uuid)
        device.update_mqtt()
        return device

    @classmethod
    def delete_device(cls, device):
        if not device:
            raise NotFoundException('Device not found')
        device.delete_from_db()
        DeviceRegistry().remove_device(device.dev_eui)
