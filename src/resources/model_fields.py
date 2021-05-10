from flask_restful import fields

point_store_fields = {
    'point_uuid': fields.String,
    'value': fields.Float,
    'value_original': fields.Float,
    'value_raw': fields.String,
    'fault': fields.Boolean,
    'fault_message': fields.String,
    'ts': fields.String
}

point_fields_only = {
    'uuid': fields.String,
    'name': fields.String,
    'device_point_name': fields.String,
    'device_uuid': fields.String,
    'enable': fields.Boolean,
    'cov_threshold': fields.Float,
    'value_round': fields.Float,
    'value_operation': fields.String,
    'created_on': fields.String,
    'updated_on': fields.String

}

point_fields = {
    **point_fields_only,
    'point_store': fields.Nested(point_store_fields)
}

device_fields = {
    'uuid': fields.String,
    'name': fields.String,
    'enable': fields.Boolean,
    'dev_eui': fields.String(),
    'device_type': fields.String(attribute="device_type.name"),
    'device_model': fields.String(attribute="device_model.name"),
    'profile_id': fields.String,
    'app_id': fields.String,
    'description': fields.String,
    'created_on': fields.String,
    'updated_on': fields.String,
    'points': fields.Nested(point_fields),

}

network_fields = {
    'name': fields.String,
    'enable': fields.Boolean,
    'ip': fields.String,
    'port': fields.Integer,
    'user': fields.String,
    'password': fields.String,

}

mapping_lp_gbp_fields = {
    'uuid': fields.String,
    'lora_point_uuid': fields.String,
    'generic_point_uuid': fields.String,
    'bacnet_point_uuid': fields.String,
    'lora_point_name': fields.String,
    'generic_point_name': fields.String,
    'bacnet_point_name': fields.String,
}
