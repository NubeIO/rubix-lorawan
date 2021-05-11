import json
import logging
import re
import uuid

from sqlalchemy.orm import validates

from src import db
from src.interfaces.device import DeviceTypes, DeviceModels
from src.models.model_base import ModelBase
from src.mqtt import MqttClient

logger = logging.getLogger(__name__)


class DeviceModel(ModelBase):
    __tablename__ = 'devices'

    uuid = db.Column(db.String(80), primary_key=True, nullable=False)
    name = db.Column(db.String(80), nullable=False, unique=True)
    enable = db.Column(db.Boolean, nullable=False, default=True)
    dev_eui = db.Column(db.String(80), nullable=False, unique=True)
    device_type = db.Column(db.Enum(DeviceTypes), nullable=False)
    device_model = db.Column(db.Enum(DeviceModels), nullable=False)
    profile_id = db.Column(db.String(120), nullable=True)
    app_id = db.Column(db.String(120), nullable=True)
    description = db.Column(db.String(120), nullable=True)
    points = db.relationship('PointModel', cascade="all,delete", backref='device', lazy=True)

    def __repr__(self):
        return "DeviceModel({})".format(self.uuid)

    @validates('name')
    def validate_name(self, _, value):
        if not re.match("^([A-Za-z0-9_-])+$", value):
            raise ValueError("name should be alphanumeric and can contain '_', '-'")
        return value

    @classmethod
    def find_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_dev_eui(cls, dev_eui: str):
        return cls.query.filter_by(dev_eui=dev_eui).first()

    def save_to_db(self):
        self.save_to_db_no_commit()
        super().save_to_db()

    def save_to_db_no_commit(self):
        if not self.points or not len(self.points):
            from src.models.device_point_presets import get_device_points
            device_points = get_device_points(self.device_model)
            for point in device_points:
                point.uuid = str(uuid.uuid4())
                point.device_point_name = point.name  # to match decoder key
                point.device_uuid = self.uuid
                point.save_to_db_no_commit()
        super().save_to_db_no_commit()

    def delete_from_db(self):
        super().delete_from_db()

    @validates('device_model', 'device_type')
    def validate_device_model(self, key, value):
        if key == 'device_type':
            if isinstance(value, DeviceTypes):
                return value
            if not value or value not in DeviceTypes.__members__:
                raise ValueError("Invalid Device Type")
            value = DeviceTypes[value]
        else:
            if not isinstance(value, DeviceModels):
                if not value or value not in DeviceModels.__members__:
                    raise ValueError("Invalid Device Model")
                value = DeviceModels[value]
        return value

    def update_mqtt(self):
        output: dict = {}
        for point in self.points:
            output[point.device_point_name] = point.point_store.value
        logger.debug(f'Publish payload: {json.dumps(output)}')
        MqttClient().publish_value((self.dev_eui, self.name), json.dumps(output))
