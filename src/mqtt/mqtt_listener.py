import logging
from abc import abstractmethod
from typing import Union, List, Callable

import gevent
from flask import current_app
from flask.ctx import AppContext
from gevent import sleep
from paho.mqtt.client import MQTTMessage
from registry.registry import RubixRegistry
from rubix_mqtt.mqtt import MqttClientBase

from src import MqttSetting
from src.handlers.exception import exception_handler

logger = logging.getLogger(__name__)


class MqttListener(MqttClientBase):
    SEPARATOR: str = '/'

    def __init__(self):
        self.__config: Union[MqttSetting, None] = None
        self.__app_context: Union[AppContext, None] = None
        MqttClientBase.__init__(self)

    @property
    def config(self) -> MqttSetting:
        return self.__config

    def start(self, config: MqttSetting, subscribe_topics: List[str] = None, callback: Callable = lambda: None):
        self.__app_context: Union[AppContext] = current_app.app_context
        self.__config = config

        subscribe_topics: List[str] = []
        if self.config.publish_value:
            topic: str = self.make_topic((self.config.topic, '#'))
            subscribe_topics.append(topic)
            gevent.spawn(self.__resubscribe_value_topic, topic)
        logger.info(f'Listening at: {subscribe_topics}')
        print(11111)
        print(subscribe_topics)
        print(11111)
        super().start(config, subscribe_topics, callback)

    def __resubscribe_value_topic(self, topic):
        """
        We resubscribe value topic for clearing un-necessary topic with retain on a certain interval of time
        For example: when we have points details on MQTT and we delete it, now it needs to be deleted from the MQTT
        broker too, this resubscribing logic does this on bulk.
        """
        while True:
            sleep(self.config.retain_clear_interval * 60)
            logger.info(f'Re-subscribing topic: {topic}')
            self.client.unsubscribe(topic)
            self.client.subscribe(topic)

    @exception_handler
    def _on_message(self, client, userdata, message: MQTTMessage):
        print(22222222)
        print(f'Listener Topic: {message.topic}, Message: {message.payload}')
        logger.debug(f'Listener Topic: {message.topic}, Message: {message.payload}')
        with self.__app_context():
            print(3333)
            if not message.payload:
                return
            print(4444)
            topic_parts: List[str] = message.topic.split(self.SEPARATOR)
            print(topic_parts)
            if len(self.make_topic((self.config.topic,)).split(self.SEPARATOR)) + 2 == len(topic_parts):
                print(5555)
                name: str = topic_parts[-1]
                dev_eui: str = topic_parts[-2]
                print(name)
                print(dev_eui)
                from src.models.model_device import DeviceModel
                if DeviceModel.find_by_name(name) is None or DeviceModel.find_by_id(dev_eui) is None:
                    print(f'No point with device.name={name}, device.dev_eui={dev_eui}')
                    logger.warning(f'No point with device.name={name}, device.dev_eui={dev_eui}')
                    self.publish_mqtt_value(message.topic, '', True)
                else:
                    logger.debug(f"Exiting point device.name={name}, device.dev_eui={dev_eui}")
                    print(f"Exiting point device.name={name}, device.dev_eui={dev_eui}")
            elif message.retain:
                logger.warning(f'Clearing topic: {message.topic}, having message: {message.payload}')
                print(f'Clearing topic: {message.topic}, having message: {message.payload}')
                self.publish_mqtt_value(message.topic, '', True)

    @abstractmethod
    def publish_mqtt_value(self, topic: str, payload: str, retain: bool = False):
        raise NotImplementedError

    @classmethod
    def prefix_topic(cls) -> str:
        wires_plat: dict = RubixRegistry().read_wires_plat()
        if not wires_plat:
            logger.error('Please add wires-plat on Rubix Service')
            return ''
        return cls.SEPARATOR.join((wires_plat.get('client_id'), wires_plat.get('client_name'),
                                   wires_plat.get('site_id'), wires_plat.get('site_name'),
                                   wires_plat.get('device_id'), wires_plat.get('device_name')))

    @classmethod
    def make_topic(cls, parts: tuple) -> str:
        return cls.SEPARATOR.join((cls.prefix_topic(),) + parts)
