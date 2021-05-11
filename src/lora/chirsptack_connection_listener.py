import logging
import time
from chirpstack import chirpstack

from src import ChirpStackSetting
from src.lora import DeviceRegistry
from src.models.model_device import DeviceModel
from src.models.model_network import NetworkModel
from src.mqtt import MqttClient
from src.utils import Singleton

logger = logging.getLogger(__name__)


class ChirpStackListener(metaclass=Singleton):
    __thread = None

    def __init__(self):
        self.__config = None
        self.__chirpstack_session = None
        self.__connection = None
        self.__network_connection = None
        self.__jwt = None
        self.__connection_status = None

    def chirpstack_session(self):
        return self.__chirpstack_session

    def chirpstack_token(self):
        return self.__jwt

    def connection_status(self):
        return self.__connection_status

    def start(self, config: ChirpStackSetting):
        self.__config = config
        self.__make_chirpstack_session()

    def __make_chirpstack_session(self):
        self.__network_connection = NetworkModel.create_network(self.__config)
        cs = self.__network_connection
        while True:
            try:
                if cs.enable:
                    time.sleep(5)  # time for mqtt client to connect
                    # Setup the connection
                    url = f"http://{self.__network_connection.ip}:{self.__network_connection.port}"
                    user = self.__network_connection.user
                    password = self.__network_connection.password
                    self.__chirpstack_session = chirpstack.Chirpstack(
                        chirpstack_url=url,
                        chirpstack_user=user,
                        chirpstack_pass=password
                    )
                    self.__jwt = self.__chirpstack_session.get_jwt()
                    self.__connection_status = self.__chirpstack_session.get_connection_status()
                    logger.info(f"ChirpStack server connected. Resuming...{self.__jwt}")
                    time.sleep(60)  # time for mqtt client to connect
                    while not self.__connection_status:
                        logger.warning(f"ChirpStack server not connected. Waiting for ChirpStack connection successful")
                        time.sleep(60)

            except Exception as e:
                self.__connection_status = None
                logger.error("Error: {}".format(str(e)))
                continue

    def __start(self):
        self.__register_devices()
        while True:
            try:
                if MqttClient().config.enabled:
                    time.sleep(1)  # time for mqtt client to connect
                    while not MqttClient().status():
                        logger.warning("MQTT not connected. Waiting for MQTT connection successful...")
                        time.sleep(MqttClient().config.attempt_reconnect_secs)
                    logger.info("MQTT client connected. Resuming..........")
            except Exception as e:
                self.__connection = None
                logger.error("Error: {}".format(str(e)))
                continue

    @staticmethod
    def __register_devices():
        for device in DeviceModel.find_all():
            DeviceRegistry().add_device(device.dev_eui, device.uuid)

    @staticmethod
    def __decode_device(data):
        if data and MqttClient().config and MqttClient().config.publish_raw:
            MqttClient().publish_raw(data)
            dev_eui = "aaa"
            device = DeviceModel.find_by_id(dev_eui)
            payload = data
            logger.debug('Sensor payload: {}'.format(payload))
            is_updated_any: bool = False
            if payload is not None:
                points = device.points
                for key in payload:
                    for point in points:
                        if key == point.device_point_name:
                            point_store = point.point_store
                            point_store.value_original = float(payload[key])
                            is_updated_any: bool = point.update_point_value(point.point_store) or is_updated_any
                if is_updated_any:
                    device.update_mqtt()
        elif data:
            logger.debug("Raw chirpstack: {}".format(data))
