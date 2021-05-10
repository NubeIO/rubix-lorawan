import uuid as uuid_
from abc import abstractmethod

from flask_restful import marshal_with, reqparse
from rubix_http.exceptions.exception import NotFoundException
from rubix_http.resource import RubixResource

from src.models.model_mapping import LPGBPointMapping
from src.models.model_point_store import PointStoreModel
from src.resources.model_fields import mapping_lp_gbp_fields


def sync_point_value(mapping: LPGBPointMapping):
    point_store: PointStoreModel = PointStoreModel.find_by_point_uuid(mapping.lora_point_uuid)
    point_store.sync_point_value_lp_to_gbp(mapping.generic_point_uuid, mapping.bacnet_point_uuid)
    return mapping


class LPGBPMappingResourceList(RubixResource):
    @classmethod
    @marshal_with(mapping_lp_gbp_fields)
    def get(cls):
        return LPGBPointMapping.find_all()

    @classmethod
    @marshal_with(mapping_lp_gbp_fields)
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('lora_point_uuid', type=str, required=True)
        parser.add_argument('generic_point_uuid', type=str, default=None)
        parser.add_argument('bacnet_point_uuid', type=str, default=None)
        parser.add_argument('lora_point_name', type=str, required=True)
        parser.add_argument('generic_point_name', type=str, default=None)
        parser.add_argument('bacnet_point_name', type=str, default=None)

        data = parser.parse_args()
        data.uuid = str(uuid_.uuid4())
        mapping: LPGBPointMapping = LPGBPointMapping(**data)
        mapping.save_to_db()
        sync_point_value(mapping)
        return mapping


class LPGBPMappingResourceBase(RubixResource):
    @classmethod
    @marshal_with(mapping_lp_gbp_fields)
    def get(cls, uuid):
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
        return mapping

    @classmethod
    def delete(cls, uuid):
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
        mapping.delete_from_db()
        return '', 204

    @classmethod
    @abstractmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        raise NotImplementedError


class LPGBPMappingResourceByUUID(LPGBPMappingResourceBase):
    parser = reqparse.RequestParser()
    parser.add_argument('lora_point_uuid', type=str)
    parser.add_argument('generic_point_uuid', type=str, default=None)
    parser.add_argument('bacnet_point_uuid', type=str, default=None)
    parser.add_argument('lora_point_name', type=str)
    parser.add_argument('generic_point_name', type=str, default=None)
    parser.add_argument('bacnet_point_name', type=str, default=None)

    @classmethod
    @marshal_with(mapping_lp_gbp_fields)
    def patch(cls, uuid):
        data = LPGBPMappingResourceByUUID.parser.parse_args()
        mapping = cls.get_mapping(uuid)
        if not mapping:
            raise NotFoundException(f'Does not exist {uuid}')
        LPGBPointMapping.filter_by_uuid(uuid).update(data)
        LPGBPointMapping.commit()
        output_mapping: LPGBPointMapping = cls.get_mapping(uuid)
        sync_point_value(output_mapping)
        return output_mapping

    @classmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        return LPGBPointMapping.find_by_uuid(uuid)


class LPGBPMappingResourceByLoRaPointUUID(LPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        return LPGBPointMapping.find_by_lora_point_uuid(uuid)


class LPGBPMappingResourceByGenericPointUUID(LPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        return LPGBPointMapping.find_by_generic_point_uuid(uuid)


class LPGBPMappingResourceByBACnetPointUUID(LPGBPMappingResourceBase):
    @classmethod
    def get_mapping(cls, uuid) -> LPGBPointMapping:
        return LPGBPointMapping.find_by_bacnet_point_uuid(uuid)
