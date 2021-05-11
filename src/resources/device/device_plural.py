import uuid
from flask_restful import marshal_with

from src.lora import ChirpStackListener
from src.models.model_device import DeviceModel
from src.resources.device.device_base import DeviceBase
from src.resources.model_fields import device_fields
from chirpstack import device


class DevicePlural(DeviceBase):
    @marshal_with(device_fields)
    def get(self):
        return DeviceModel.find_all()

    def post(self):
        uuid_ = str(uuid.uuid4())
        cs = ChirpStackListener().chirpstack_session()
        cs_status = ChirpStackListener().connection_status()
        data = DevicePlural.parser.parse_args()
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
            res = d.create_and_activate()
            if res.get("result") == "success":
                return self.add_device(uuid_, data)
            elif res.get("result") == "failure":
                return res
        else:
            return {"result": "no connection to server"}
