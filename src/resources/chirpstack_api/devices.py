from chirpstack import device
from rubix_http.resource import RubixResource
from src.lora import ChirpStackListener


def _get_connection():
    cs = ChirpStackListener().chirpstack_session()
    return device.Devices(chirpstack_connection=cs)


class ChirpStackDevice(RubixResource):
    def get(self, **kwargs):
        dev_eui = kwargs.get('dev_eui')
        return _get_connection().get_device(dev_eui=dev_eui)


class ChirpStackDevices(RubixResource):
    def get(self, **kwargs):
        app_id = kwargs.get('app_id')
        return _get_connection().list_all(appid=app_id)


