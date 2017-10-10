import json

from flask import g, url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import Data
from ..queries import query_get_data_by_id

@api.route('/data', methods=['POST'])
def add_data():
    data = Data.from_dict(json.loads(request.data))
    db.session.add(data)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(data.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_data', id=data.id)
    return resp

@api.route('/data/batch', methods=['POST'])
def add_batch_data():
    request_data = json.loads(request.data)
    sensor_id = request_data['sensor_id']
    values = request_data['value']
    for value in values:
        data = Data.from_dict({'sensor_id': sensor_id, 'value': value})
        db.session.add(data)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 201

@api.route('/data/<id>', methods=['GET'])
def get_data(id):
    data = query_get_data_by_id(id, g.current_user.id)
    return jsonify(data.to_dict())
