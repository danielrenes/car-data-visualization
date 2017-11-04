import json

from flask import g, url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import ViewWrapper, View, Subview
from ..queries import query_all_views, query_get_view_by_id, query_get_sensor_by_name

@api.route('/views', methods=['GET'])
def get_views():
    return jsonify({'views': [view.to_dict() for view in query_all_views(g.current_user.id)]})

@api.route('/view/<id>', methods=['GET'])
def get_view(id):
    view = query_get_view_by_id(id, g.current_user.id)
    return jsonify(view.to_dict())

@api.route('/view', methods=['POST'])
def add_view():
    view = ViewWrapper.from_dict(json.loads(request.data))
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

@api.route('/view/dynamic/add', methods=['GET'])
def add_dynamic_view():
    sensor_name = request.args.get('sensor_name')
    sensor_id = query_get_sensor_by_name(sensor_name, g.current_user.id).id
    view = View.from_dict({
        'name':         'dynamic',
        'count':        1,
        'refresh_time': 10,
        'user_id':      g.current_user.id
    })
    db.session.add(view)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    subview = Subview.from_dict({
        'sensor_id':        sensor_id,
        'chartconfig_id':   1,
        'view_id':          view.id
    })
    db.session.add(subview)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify({'view_id': view.id})
    resp.status_code = 201
    return resp

@api.route('/view/dynamic/remove', methods=['GET'])
def remove_dynamic_view():
    view_id = request.args.get('view_id')
    db.session.delete(query_get_view_by_id(view_id, g.current_user.id))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 204
