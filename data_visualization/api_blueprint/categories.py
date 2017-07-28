import json

from flask import url_for, jsonify, abort, request
from sqlalchemy.exc import IntegrityError

from . import api
from .. import db
from ..models import Category
from ..queries import all_categories

@api.route('/categories', methods=['GET'])
def get_categories():
    categs = all_categories().order_by(Category.id).all()
    return jsonify({'categories': [categ.to_dict() for categ in categs]})

@api.route('/category', methods=['POST'])
def add_category():
    categ = Category.from_dict(json.loads(request.data))
    db.session.add(categ)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(categ.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('api.get_category', id=categ.id)
    return resp

@api.route('/category/<id>', methods=['GET'])
def get_category(id):
    categ = all_categories().filter(Category.id==id).first()
    if categ is None:
        abort(400)
    return jsonify(categ.to_dict())

@api.route('/category/<id>', methods=['DELETE'])
def remove_category(id):
    categ = all_categories().filter(Category.id==id).first()
    if categ is None:
        abort(400)
    db.session.delete(categ)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify('')
    resp.status_code = 204
    return resp

@api.route('/category/<id>', methods=['PUT'])
def modify_category(id):
    categ = all_categories().filter(Category.id==id).first()
    for key, value in json.loads(request.data).iteritems():
        if key is not 'id':
            setattr(categ, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify(categ.to_dict())
    resp.status_code = 201
    return resp
