import json

from flask import url_for, jsonify, abort, request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import User
from ..queries import all_users

@api.route('/user', methods=['POST'])
def add_user():
    user = User.from_dict(json.loads(request.data))
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(user.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_user', id=user.id)
    return resp

@api.route('/user', methods=['GET'])
@login_required
def get_user():
    user = all_users().filter(User.id==current_user.id).first()
    if user is None:
        abort(400)
    return jsonify(user.to_dict())

@api.route('/user', methods=['PUT'])
@login_required
def modify_user(id):
    user = all_users().filter(User.id==current_user.id).first()
    if user is None:
        abort(400)
    for key, value in json.loads(request.data).iteritems():
        if key is not 'id':
            setattr(user, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(user.to_dict())
    resp.status_code = 201
    return resp

@api.route('/user', methods=['DELETE'])
@login_required
def remove_user(id):
    user = all_users().filter(User.id==current_user.id).first()
    if user is None:
        abort(400)
    db.session.delete(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 204
