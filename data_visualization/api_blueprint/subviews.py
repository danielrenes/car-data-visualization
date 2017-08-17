import json

from flask import g, url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import Subview, View
from ..queries import query_get_subview_by_id, query_get_view_by_id

@api.route('/subview/<id>', methods=['GET'])
def get_subview(id):
    subview = query_get_subview_by_id(id, g.current_user.id)
    return jsonify(subview.to_dict())

@api.route('/subview', methods=['POST'])
def add_subview():
    subview = Subview.from_dict(json.loads(request.data))
    db.session.add(subview)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(subview.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_subview', id=subview.id)
    return resp

@api.route('/subview/<id>', methods=['PUT'])
def modify_subview(id):
    subview = query_get_subview_by_id(id, g.current_user.id)
    request_data = json.loads(request.data)
    if 'view_id' in request_data.iterkeys():
        view = query_get_view_by_id(request_data['view_id'], g.current_user.id)
        if subview.view_id != request_data['view_id'] and view.is_full():
            abort(400)
    for key, value in request_data.iteritems():
        if key is not 'id':
            setattr(subview, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(subview.to_dict())
    resp.status_code = 201
    return resp

@api.route('/subview/<id>', methods=['DELETE'])
def remove_subview(id):
    subview = query_get_subview_by_id(id, g.current_user.id)
    db.session.delete(subview)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 204
