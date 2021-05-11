from chirpstack import device
from rubix_http.resource import RubixResource
from src.lora import ChirpStackListener


class ChirpStackApiDevice(RubixResource):
    @staticmethod
    def get_connection():
        cs = ChirpStackListener().chirpstack_session()
        return device.Devices(chirpstack_connection=cs)

    @staticmethod
    def get_connection_status():
        return ChirpStackListener().connection_status()


class ChirpStackDevice(RubixResource):
    def get(self, **kwargs):
        dev_eui = kwargs.get('dev_eui')
        if ChirpStackApiDevice().get_connection_status():
            return ChirpStackApiDevice().get_connection().get_device(dev_eui=dev_eui)
        else:
            return {"status": "fail"}


class ChirpStackDevices(RubixResource):
    def get(self, **kwargs):
        app_id = kwargs.get('app_id')
        if ChirpStackApiDevice().get_connection_status():
            return ChirpStackApiDevice().get_connection().list_all(appid=app_id)
        else:
            return {"status": "fail"}
