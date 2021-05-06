from flask import Blueprint
from flask_restful import Api
from src.resources.ping import Ping
from src.services.check_host import STM

bp_system = Blueprint('system', __name__, url_prefix='/api/system')
Api(bp_system).add_resource(Ping, '/ping')

bp_gpio = Blueprint('gpio', __name__, url_prefix='/api/gpio')
Api(bp_gpio).add_resource(STM, '/rc/stm')
