import json

from flask import g, url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import View
from ..queries import query_all_views, query_get_view_by_id

@api.route('/views', methods=['GET'])
def get_views():
    return jsonify({'views': [view.to_dict() for view in query_all_views(g.current_user.id)]})

@api.route('/view/<id>', methods=['GET'])
def get_view(id):
    view = query_get_view_by_id(id, g.current_user.id)
    return jsonify(view.to_dict())

@api.route('/view', methods=['POST'])
def add_view():
    view = View.from_dict(json.loads(request.data))
    db.session.add(view)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(view.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_view', id=view.id)
    return resp

@api.route('/view/<id>', methods=['PUT'])
def modify_view(id):
    view = query_get_view_by_id(id, g.current_user.id)
    request_data = json.loads(request.data)
    if 'count' in request_data.iterkeys():
        if not view.check_count(request_data['count']):
            abort(400)
    if 'refresh_time' in request_data.iterkeys():
        if not view.check_refresh_time(request_data['refresh_time']):
            abort(400)
    for key, value in request_data.iteritems():
        if key is not 'id':
            setattr(view, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(view.to_dict())
    resp.status_code = 201
    return resp

@api.route('/view/<id>', methods=['DELETE'])
def remove_view(id):
    view = query_get_view_by_id(id, g.current_user.id)
    db.session.delete(view)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 204
