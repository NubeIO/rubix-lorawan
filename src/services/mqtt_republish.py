import logging
from typing import List

from gevent import thread

from src.models.model_device import DeviceModel
from src.mqtt import MqttClient
from src.utils import Singleton

logger = logging.getLogger(__name__)


class MqttRepublish(metaclass=Singleton):
    def republish(self):
        logger.info(f"Called MQTT republish")
        while not MqttClient().status():
            logger.warning('Waiting for MQTT connection to be connected...')
            thread.sleep(2)
        self._publish_devices()
        logger.info(f"Finished MQTT republish")

    @staticmethod
    def _publish_devices():
        devices: List[DeviceModel] = DeviceModel.find_all()
        for device in devices:
            device.update_mqtt()
