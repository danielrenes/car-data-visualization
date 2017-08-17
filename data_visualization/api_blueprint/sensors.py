import json

from flask import g, url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import Sensor
from ..queries import query_all_sensors, query_get_sensor_by_id

@api.route('/sensors', methods=['GET'])
def get_sensors():
    return jsonify({'sensors': [sensor.to_dict() for sensor in query_all_sensors(g.current_user.id)]})

@api.route('/sensor', methods=['POST'])
def add_sensor():
    sensor = Sensor.from_dict(json.loads(request.data))
    db.session.add(sensor)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(sensor.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_sensor', id=sensor.id)
    return resp

@api.route('/sensor/<id>', methods=['GET'])
def get_sensor(id):
    sensor = query_get_sensor_by_id(id, g.current_user.id)
    return jsonify(sensor.to_dict())

@api.route('/sensor/<id>', methods=['DELETE'])
def remove_sensor(id):
    sensor = query_get_sensor_by_id(id, g.current_user.id)
    db.session.delete(sensor)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 204

@api.route('/sensor/<id>', methods=['PUT'])
def modify_sensor(id):
    sensor = query_get_sensor_by_id(id, g.current_user.id)
    for key, value in json.loads(request.data).iteritems():
        if key is not 'id':
            setattr(sensor, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(sensor.to_dict())
    resp.status_code = 201
    return resp
