import json
import os
from abc import ABC

from flask import Flask
from rubix_mqtt.setting import MqttSettingBase


class BaseSetting(ABC):

    def reload(self, setting: dict):
        if setting is not None:
            self.__dict__ = {k: setting.get(k, v) for k, v in self.__dict__.items()}
        return self

    def serialize(self, pretty=True) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=2 if pretty else None)

    def to_dict(self):
        return json.loads(self.serialize(pretty=False))


class ChirpStackSetting(BaseSetting):
    KEY = 'ChirpStack'

    def __init__(self):
        self.enable: bool = True
        self.name: str = 'lorawan'
        self.ip: str = '0.0.0.0'
        self.port = 8080
        self.user: str = 'admin'
        self.password: str = 'admin'


class MqttSetting(MqttSettingBase):
    KEY = 'mqtt'

    def __init__(self):
        super().__init__()
        self.name = 'lora-raw-mqtt'
        self.attempt_reconnect_secs = 5
        self.retain_clear_interval = 10
        self.publish_value = True
        self.topic = 'rubix/lora_raw/value'
        self.subscribe_topic = 'application/+/device/+/rx'
        self.publish_raw = True
        self.raw_topic = 'rubix/lora_raw/raw'
        self.publish_debug = True
        self.debug_topic = 'rubix/lora_raw/debug'


class AppSetting:
    PORT = 1919
    FLASK_KEY: str = 'APP_SETTING'
    GLOBAL_DIR_ENV = 'RUBIX_LORA_GLOBAL'
    DATA_DIR_ENV = 'RUBIX_LORA_DATA'
    CONFIG_DIR_ENV = 'RUBIX_LORA_CONFIG'
    default_global_dir: str = 'out'
    default_data_dir: str = 'data'
    default_config_dir: str = 'config'
    default_identifier: str = 'lora'
    default_setting_file: str = 'config.json'
    default_logging_conf: str = 'logging.conf'
    fallback_logging_conf: str = 'config/logging.example.conf'
    fallback_prod_logging_conf: str = 'config/logging.prod.example.conf'

    def __init__(self, **kwargs):
        self.__port = kwargs.get('port') or AppSetting.PORT
        self.__global_dir = self.__compute_dir(kwargs.get('global_dir'), AppSetting.default_global_dir, 0o777)
        self.__data_dir = self.__compute_dir(self.__join_global_dir(kwargs.get('data_dir')),
                                             self.__join_global_dir(AppSetting.default_data_dir))
        self.__config_dir = self.__compute_dir(self.__join_global_dir(kwargs.get('config_dir')),
                                               self.__join_global_dir(AppSetting.default_config_dir))
        self.__identifier = kwargs.get('identifier') or AppSetting.default_identifier
        self.__prod = kwargs.get('prod') or False
        self.__mqtt_setting = MqttSetting()
        self.chirpstack_setting = ChirpStackSetting()

    @property
    def port(self):
        return self.__port

    @property
    def global_dir(self):
        return self.__global_dir

    @property
    def data_dir(self):
        return self.__data_dir

    @property
    def config_dir(self):
        return self.__config_dir

    @property
    def identifier(self):
        return self.__identifier

    @property
    def prod(self) -> bool:
        return self.__prod

    @property
    def mqtt(self) -> MqttSetting:
        return self.__mqtt_setting

    @property
    def chirpstack(self) -> ChirpStackSetting:
        return self.chirpstack_setting

    def serialize(self, pretty=True) -> str:
        m = {MqttSetting.KEY: self.mqtt, ChirpStackSetting.KEY: self.chirpstack, 'prod': self.prod,
             'global_dir': self.global_dir, 'data_dir': self.data_dir, 'config_dir': self.config_dir}
        return json.dumps(m, default=lambda o: o.to_dict() if isinstance(o, BaseSetting) else o.__dict__,
                          indent=2 if pretty else None)

    def reload(self, setting_file: str, is_json_str: bool = False):
        data = self.__read_file(setting_file, self.__config_dir, is_json_str)
        self.__mqtt_setting = self.__mqtt_setting.reload(data.get(MqttSetting.KEY, None))
        self.chirpstack_setting = self.chirpstack_setting.reload(data.get(ChirpStackSetting.KEY, None))
        return self

    def init_app(self, app: Flask):
        app.config[AppSetting.FLASK_KEY] = self
        return self

    def __join_global_dir(self, _dir):
        return _dir if _dir is None or _dir.strip() == '' else os.path.join(self.__global_dir, _dir)

    @staticmethod
    def __compute_dir(_dir: str, _def: str, mode=0o744) -> str:
        d = os.path.join(os.getcwd(), _def) if _dir is None or _dir.strip() == '' else _dir
        d = d if os.path.isabs(d) else os.path.join(os.getcwd(), d)
        os.makedirs(d, mode, True)
        return d

    @staticmethod
    def __read_file(setting_file: str, _dir: str, is_json_str=False):
        if is_json_str:
            return json.loads(setting_file)
        if setting_file is None or setting_file.strip() == '':
            return {}
        s = setting_file if os.path.isabs(setting_file) else os.path.join(_dir, setting_file)
        if not os.path.isfile(s) or not os.path.exists(s):
            return {}
        with open(s) as json_file:
            return json.load(json_file)
