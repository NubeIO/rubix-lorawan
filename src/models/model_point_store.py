from ast import literal_eval
from typing import List

import gevent
from rubix_http.method import HttpMethod
from rubix_http.request import gw_request
from sqlalchemy import and_, or_

from src import db
from src.models.model_mapping import LPGBPointMapping


class PointStoreModelMixin(object):
    value = db.Column(db.Float(), nullable=True)
    value_original = db.Column(db.Float(), nullable=True)
    value_raw = db.Column(db.String(), nullable=True)
    fault = db.Column(db.Boolean(), default=False, nullable=False)
    fault_message = db.Column(db.String())
    ts = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class PointStoreModel(PointStoreModelMixin, db.Model):
    __tablename__ = 'point_stores'
    point_uuid = db.Column(db.String, db.ForeignKey('points.uuid'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"PointStore(point_uuid = {self.point_uuid})"

    @classmethod
    def find_by_point_uuid(cls, point_uuid: str):
        return cls.query.filter_by(point_uuid=point_uuid).first()

    @classmethod
    def create_new_point_store_model(cls, point_uuid: str):
        return PointStoreModel(point_uuid=point_uuid, value_original=None, value=None, value_raw="")

    def raw_value(self) -> any:
        """Parse value from value_raw"""
        if self.value_raw:
            value_raw = literal_eval(self.value_raw)
            return value_raw
        else:
            return None

    def update(self, cov_threshold: float = None) -> bool:
        if not self.fault:
            self.fault = bool(self.fault)
            res = db.session.execute(
                self.__table__
                    .update()
                    .values(value=self.value,
                            value_original=self.value_original,
                            value_raw=self.value_raw,
                            fault=False,
                            fault_message=None)
                    .where(and_(self.__table__.c.point_uuid == self.point_uuid,
                                or_(self.__table__.c.value == None,
                                    db.func.abs(self.__table__.c.value - self.value) >= cov_threshold,
                                    self.__table__.c.fault != self.fault))))
        else:
            res = db.session.execute(
                self.__table__
                    .update()
                    .values(fault=self.fault, fault_message=self.fault_message)
                    .where(and_(self.__table__.c.point_uuid == self.point_uuid,
                                or_(self.__table__.c.fault != self.fault,
                                    self.__table__.c.fault_message != self.fault_message))))
        db.session.commit()
        updated: bool = bool(res.rowcount)
        if updated:
            """LoRa > Generic | BACnet point value"""
            self.__sync_point_value_lp_to_gbp_process()
        return updated

    def sync_point_value_lp_to_gbp(self, generic_point_uuid: str, bacnet_point_uuid: str, gp: bool = True, bp=True):
        if generic_point_uuid and gp:
            gw_request(
                api=f"/ps/api/generic/points_value/uuid/{generic_point_uuid}",
                body={"value": self.value},
                http_method=HttpMethod.PATCH
            )
        elif bacnet_point_uuid and bp:
            gw_request(
                api=f"/bacnet/api/bacnet/points/uuid/{bacnet_point_uuid}",
                body={"priority_array_write": {"_16": self.value}},
                http_method=HttpMethod.PATCH
            )

    def __sync_point_value_lp_to_gbp_process(self, gp: bool = True, bp=True):
        mapping: LPGBPointMapping = LPGBPointMapping.find_by_lora_point_uuid(self.point_uuid)
        if mapping:
            gevent.spawn(self.sync_point_value_lp_to_gbp,
                         mapping.generic_point_uuid, mapping.bacnet_point_uuid, gp, bp)

    @classmethod
    def sync_points_values_lp_to_gbp_process(cls, gp: bool = True, bp=True):
        mappings: List[LPGBPointMapping] = LPGBPointMapping.find_all()
        for mapping in mappings:
            point_store: PointStoreModel = PointStoreModel.find_by_point_uuid(mapping.lora_point_uuid)
            if point_store:
                point_store.__sync_point_value_lp_to_gbp_process(gp=gp, bp=bp)
