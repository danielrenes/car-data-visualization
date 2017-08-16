import json

from flask import g, url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import User
from ..queries import all_users

@api.route('/user', methods=['GET'])
def get_user():
    user = User.query.get_or_404(g.current_user.id)
    return jsonify(user.to_dict())

@api.route('/user', methods=['PUT'])
def modify_user():
    user = User.query.get_or_404(g.current_user.id)
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
def remove_user():
    user = User.query.get_or_404(g.current_user.id)
    db.session.delete(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 204
