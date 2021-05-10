from flask import current_app
from flask_restful import reqparse, marshal_with
from rubix_http.resource import RubixResource

from src import AppSetting
from src.lora import ChirpStackListener
from src.models.model_network import NetworkModel
from src.resources.model_fields import network_fields


class NetworkDriver(RubixResource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, store_missing=False)
    parser.add_argument('enable', type=bool, store_missing=False)
    parser.add_argument('ip', type=str, store_missing=False)
    parser.add_argument('port', type=int, store_missing=False)
    parser.add_argument('user', type=str, store_missing=False)
    parser.add_argument('password', type=str, store_missing=False)

    @marshal_with(network_fields)
    def get(self):
        print(ChirpStackListener().chirpstack_token())

        return NetworkModel.find_one()

    @marshal_with(network_fields)
    def patch(self):
        data = NetworkDriver.parser.parse_args()
        NetworkModel.filter_one().update(data)
        new_network_driver = NetworkModel.find_one()
        NetworkModel.commit()
        return new_network_driver
