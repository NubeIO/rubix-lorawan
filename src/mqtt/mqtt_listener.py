import json
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
            subscribe_topic: str = self.config.subscribe_topic
            subscribe_topics.append(topic)
            subscribe_topics.append(subscribe_topic)
            gevent.spawn(self.__resubscribe_value_topic, topic)
        logger.info(f'Listening at: {subscribe_topics}')
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
        print(f'Listener Topic: {message.topic}, Message: {message.payload}')
        logger.debug(f'Listener Topic: {message.topic}, Message: {message.payload}')
        with self.__app_context():
            if not message.payload:
                return
            topic_parts: List[str] = message.topic.split(self.SEPARATOR)
            if topic_parts[0] == "application" and topic_parts[2] == "device" and topic_parts[4] == "rx":
                payload = json.loads(message.payload)
                name: str = payload.get('deviceName')
                rx_info = payload.get('rxInfo')
                rssi = 123
                print(name)
                dev_eui: str = topic_parts[-2]
                logger.debug(f'Listener dev_eui: {dev_eui}, Message: {payload}')
                from src.models.model_device import DeviceModel
                # if True:
                if DeviceModel.find_by_dev_eui(dev_eui):
                    from src.lora import ChirpStackListener
                    logger.warning(f'point with device.name={name}, device.dev_eui={dev_eui}')
                    ChirpStackListener.decode_mqtt_payload(payload, dev_eui, rssi)
                else:
                    print(f'No point with device.name={name}, device.dev_eui={dev_eui}')
                    logger.warning(f'No point with device.name={name}, device.dev_eui={dev_eui}')

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


    # @staticmethod
    # def __decode_device(payload, dev_eui):
    #     device = DeviceModel.find_by_id(dev_eui)
    #     logger.debug('Sensor payload: {}'.format(payload))
    #     is_updated_any: bool = False
    #     if payload is not None:
    #         points = device.points
    #         for key in payload:
    #             for point in points:
    #                 if key == point.device_point_name:
    #                     point_store = point.point_store
    #                     point_store.value_original = float(payload[key])
    #                     is_updated_any: bool = point.update_point_value(point.point_store) or is_updated_any
    #         if is_updated_any:
    #             device.update_mqtt()


