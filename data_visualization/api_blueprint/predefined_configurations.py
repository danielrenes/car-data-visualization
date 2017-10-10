import json

from flask import jsonify, abort, request, url_for

from . import api
from .. import db
from ..models import PredefinedConfiguration
from ..queries import query_all_predefined_configs, query_get_predefined_config_by_id

@api.route('/predefinedconfigs', methods=['GET'])
def get_predefined_configs():
    predefined_configs = query_all_predefined_configs()
    return jsonify({'predefined_configs': [predefined_config.to_dict() for predefined_config in predefined_configs]})

@api.route('/predefinedconfig/<id>', methods=['GET'])
def get_predefined_config(id):
    predefined_config = query_get_predefined_config_by_id(id)
    return jsonify(predefined_config.to_dict())

@api.route('/predefinedconfigs', methods=['POST'])
def add_predefined_config():
    predefined_config = PredefinedConfiguration.from_dict(json.loads(request.data))
    db.session.add(predefined_config)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(predefined_config.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_predefined_config', id=predefined_config.id)
    return resp
