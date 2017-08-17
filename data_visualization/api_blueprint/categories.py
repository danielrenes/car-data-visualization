import json

from flask import g, url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import Category
from ..queries import query_get_category_by_id, query_all_categories

@api.route('/categories', methods=['GET'])
def get_categories():
    return jsonify({'categories': [category.to_dict() for category in query_all_categories(g.current_user.id)]})

@api.route('/category', methods=['POST'])
def add_category():
    category = Category.from_dict(json.loads(request.data))
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(category.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_category', id=category.id)
    return resp

@api.route('/category/<id>', methods=['GET'])
def get_category(id):
    category = query_get_category_by_id(id, g.current_user.id)
    return jsonify(category.to_dict())

@api.route('/category/<id>', methods=['DELETE'])
def remove_category(id):
    category = query_get_category_by_id(id, g.current_user.id)
    db.session.delete(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    return '', 204

@api.route('/category/<id>', methods=['PUT'])
def modify_category(id):
    category = query_get_category_by_id(id, g.current_user.id)
    for key, value in json.loads(request.data).iteritems():
        if key is not 'id':
            setattr(category, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(category.to_dict())
    resp.status_code = 201
    return resp
