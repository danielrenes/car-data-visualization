import json

from flask import url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import Sensor
from ..queries import all_sensors

@api.route('/sensors', methods=['GET'])
def get_sensors():
    sens = all_sensors().order_by(Sensor.id).all()
    return jsonify({'sensors': [sen.to_dict() for sen in sens]})

@api.route('/sensor', methods=['POST'])
def add_sensor():
    sen = Sensor.from_dict(json.loads(request.data))
    db.session.add(sen)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(sen.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_sensor', id=sen.id)
    return resp

@api.route('/sensor/<id>', methods=['GET'])
def get_sensor(id):
    sen = all_sensors().filter(Sensor.id==id).first()
    if sen is None:
        abort(400)
    return jsonify(sen.to_dict())

@api.route('/sensor/<id>', methods=['DELETE'])
def remove_sensor(id):
    sen = all_sensors().filter(Sensor.id==id).first()
    if sen is None:
        abort(400)
    db.session.delete(sen)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 204

@api.route('/sensor/<id>', methods=['PUT'])
def modify_sensor(id):
    sen = all_sensors().filter(Sensor.id==id).first()
    if sen is None:
        abort(400)
    for key, value in json.loads(request.data).iteritems():
        if key is not 'id':
            setattr(sen, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(sen.to_dict())
    resp.status_code = 201
    return resp
