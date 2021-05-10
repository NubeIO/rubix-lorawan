import json
import random
import re

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates

from src import db
from src.models.model_base import ModelBase
from src.models.model_device import DeviceModel
from src.models.model_network import NetworkModel
from src.models.model_point_store import PointStoreModel
from src.mqtt import MqttClient
from src.utils.math_functions import eval_arithmetic_expression


class PointModel(ModelBase):
    __tablename__ = 'points'

    uuid = db.Column(db.String(80), primary_key=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    device_uuid = db.Column(db.String, db.ForeignKey('devices.uuid'), nullable=False)
    enable = db.Column(db.Boolean(), nullable=False, default=True)
    device_point_name = db.Column(db.String(), nullable=False)
    cov_threshold = db.Column(db.Float, nullable=False, default=0)
    value_round = db.Column(db.Integer(), nullable=False, default=2)
    value_operation = db.Column(db.String, nullable=True, default="x + 0")
    point_store = db.relationship('PointStoreModel', backref='point', lazy=False, uselist=False, cascade="all,delete")
    lp_gbp_mapping = db.relationship('LPGBPointMapping', backref='point', lazy=True, uselist=False,
                                     cascade="all,delete")

    __table_args__ = (
        UniqueConstraint('name', 'device_uuid'),
    )

    def __repr__(self):
        return f"Point(uuid = {self.uuid})"

    @validates('name')
    def validate_name(self, _, value):
        if not re.match("^([A-Za-z0-9_-])+$", value):
            raise ValueError("name should be alphanumeric and can contain '_', '-'")
        return value

    @validates('value_operation')
    def validate_value_operation(self, _, value):
        try:
            if value and value.strip():
                eval_arithmetic_expression(value.lower().replace('x', str(random.randint(1, 9))))
        except Exception:
            raise ValueError("Invalid value_operation, must be a valid arithmetic expression")
        return value

    @classmethod
    def find_by_name(cls, device_name: str, point_name: str):
        results = cls.query.filter_by(name=point_name) \
            .join(DeviceModel).filter_by(name=device_name) \
            .first()
        return results

    def save_to_db(self):
        self.point_store = PointStoreModel.create_new_point_store_model(self.uuid)
        super().save_to_db()

    def save_to_db_no_commit(self):
        self.point_store = PointStoreModel.create_new_point_store_model(self.uuid)
        super().save_to_db_no_commit()

    def update(self, **kwargs):
        super().update(**kwargs)
        point_store: PointStoreModel = PointStoreModel.find_by_point_uuid(self.uuid)
        is_updated: bool = self.update_point_value(point_store, 0)
        if is_updated:
            self.device.update_mqtt()
        self.point_store = point_store
        return self

    def update_point_value(self, point_store: PointStoreModel, cov_threshold: float = None) -> bool:
        if not point_store.fault:
            if cov_threshold is None:
                cov_threshold = self.cov_threshold
            value = point_store.value_original
            device = DeviceModel.find_by_uuid(self.device_uuid)
            device_type = device.device_type
            if value is not None:
                value = self.apply_value_operation(value, self.value_operation)
                if value is not None:
                    value = round(value, self.value_round)
            point_store.value = value
        return point_store.update(cov_threshold)

    @classmethod
    def apply_value_operation(cls, original_value: float, value_operation: str) -> float or None:
        """Do calculations on original value with the help of point details"""
        if original_value is None or value_operation is None or not value_operation.strip():
            return original_value
        return eval_arithmetic_expression(value_operation.lower().replace('x', str(original_value)))

    def publish_cov(self, point_store: PointStoreModel, device: DeviceModel = None, network: NetworkModel = None,
                    service_name: str = None):
        pass
