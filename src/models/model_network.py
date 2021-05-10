import re
import uuid
from sqlalchemy.orm import validates

from src import db, ChirpStackSetting
from src.models.model_base import ModelBase


class NetworkModel(ModelBase):
    __tablename__ = 'network'

    uuid = db.Column(db.String(80), primary_key=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    enable = db.Column(db.Boolean(), nullable=False, default=True)
    ip = db.Column(db.String(120), nullable=False)
    port = db.Column(db.Integer(), nullable=False, unique=True)
    user = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    @validates('name')
    def validate_name(self, _, value):
        if not re.match("^([A-Za-z0-9_-])+$", value):
            raise ValueError("name should be alphanumeric and can contain '_', '-'")
        return value

    @classmethod
    def filter_one(cls):
        return cls.query.filter()

    @classmethod
    def find_one(cls):
        driver = cls.query.first()
        if driver:
            db.session.refresh(driver)
        return driver

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def create_network(cls, config: ChirpStackSetting):
        n = NetworkModel.find_one()
        if not n:
            uuid_ = str(uuid.uuid4())
            n = NetworkModel(uuid=uuid_,
                             name=config.name,
                             enable=config.enable,
                             ip=config.ip,
                             port=config.port,
                             user=config.user,
                             password=config.password)

            n.save_to_db()
        else:
            db.session.refresh(n)

        return n

    @validates('port')
    def validate_name(self, _, value):
        self.name = value
        return value
