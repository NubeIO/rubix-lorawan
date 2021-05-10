import logging
from src import MqttSetting
from src.mqtt.mqtt_listener import MqttListener
from src.utils import Singleton

logger = logging.getLogger(__name__)


def allow_only_on_prefix(func):
    def inner_function(*args, **kwargs):
        prefix_topic: str = MqttClient.prefix_topic()
        if not prefix_topic:
            return
        func(*args, **kwargs)

    return inner_function


class MqttClient(MqttListener, metaclass=Singleton):
    SEPARATOR: str = '/'

    @property
    def config(self) -> MqttSetting:
        return super().config if isinstance(super().config, MqttSetting) else MqttSetting()

    @allow_only_on_prefix
    def publish_value(self, topic_suffix: tuple, payload: str):
        if self.config.publish_value:
            self.publish_mqtt_value(self.make_topic((self.config.topic,) + topic_suffix), payload, True)

    @allow_only_on_prefix
    def publish_raw(self, payload: str):
        if self.config.publish_raw:
            self.publish_mqtt_value(self.make_topic((self.config.raw_topic,)), payload)

    @allow_only_on_prefix
    def publish_debug(self, payload: str):
        if self.config.publish_debug:
            self.publish_mqtt_value(self.make_topic((self.config.debug_topic,)), payload)

    def publish_mqtt_value(self, topic: str, payload: str, retain: bool = False):
        if not self.status():
            logger.error(f"MQTT client {self.to_string()} is not connected...")
            return
        logger.debug(f"MQTT_PUBLISH: 'topic': {topic}, 'payload': {payload}, 'retain': {retain}")
        self.client.publish(topic, str(payload), qos=self.config.qos, retain=retain)
