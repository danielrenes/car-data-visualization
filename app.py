#!/usr/bin/env python

import datetime
import json
import os
import sys

from flask import Flask, render_template, redirect, url_for, request, jsonify, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only
from wtforms import StringField, IntegerField, HiddenField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional, Length, IPAddress, NumberRange, AnyOf

import chartjs

# init

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') if 'SECRET_KEY' in os.environ else 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI') if 'DATABASE_URI' in os.environ else 'sqlite://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True
db = SQLAlchemy(app)

# models

def check_keys(legal_keys, keys):
    if len(keys) > len(legal_keys):
        abort(400)
    found_keys = []
    for key in keys:
        if key not in legal_keys:
            abort(400)
        if key in found_keys:
            abort(400)
        found_keys.append(key)

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20), unique=True, nullable=False)
    min_value = db.Column(db.Integer, nullable=False)
    max_value = db.Column(db.Integer, nullable=False)

    sensors = db.relationship('Sensor', backref='category', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'links': {
                'self': url_for('get_category', id=self.id),
                'form_add': url_for('add_category_form'),
                'form_edit': url_for('edit_category_form', id=self.id),
                'sensors': [url_for('get_sensor', id=sensor.id) for sensor in self.sensors]
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['name', 'min_value', 'max_value']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        categ = Category()
        for key in data_keys:
            setattr(categ, key, data[key])
        return categ

class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20), unique=True, nullable=False)
    location = db.Column(db.String(40))
    ipv4_addr = db.Column(db.String(15), unique=True)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    datas = db.relationship('Data', backref='sensor', lazy='dynamic', cascade='all, delete-orphan')
    subviews = db.relationship('Subview', backref='sensor', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'location': self.location,
            'ipv4_addr': self.ipv4_addr,
            'links': {
                'self': url_for('get_sensor', id=self.id),
                'form_add': url_for('add_sensor_form'),
                'form_edit': url_for('edit_sensor_form', id=self.id),
                'category': url_for('get_category', id=self.category_id),
                'datas': [url_for('get_data', id=data.id) for data in self.datas],
                'subviews': [url_for('get_subview', id=subview.id) for subview in self.subviews]
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['name', 'category_id', 'location', 'ipv4_addr']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        sen = Sensor()
        for key in data_keys:
            setattr(sen, key, data[key])
        return sen

    def __str__(self):
        return self.name

class Data(db.Model):
    __tablename__ = 'data-points'

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'timestamp': self.timestamp,
            'sensor_id': self.sensor_id,
            'links': {
                'self': url_for('get_data', id=self.id),
                'sensor': url_for('get_sensor', id=self.sensor_id)
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['value', 'sensor_id']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        dat = Data()
        for key in data_keys:
            setattr(dat, key, data[key])
        return dat

class ChartConfig(db.Model):
    __tablename__ = 'chartconfigs'

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(20), nullable=False)

    subviews = db.relationship('Subview', backref='chartconfig', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'links': {
                'self': url_for('get_chartconfig', id=self.id),
                'subviews': [url_for('get_subview', id=subview.id) for subview in self.subviews]
            }
        }

    def __str__(self):
        return self.type

class Subview(db.Model):
    __tablename__ = 'subviews'

    id = db.Column(db.Integer, primary_key=True)

    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)
    chartconfig_id = db.Column(db.Integer, db.ForeignKey('chartconfigs.id'), nullable=False)
    view_id = db.Column(db.Integer, db.ForeignKey('views.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'chartconfig_id': self.chartconfig_id,
            'view_id': self.view_id,
            'links': {
                'self': url_for('get_subview', id=self.id),
                'form_add': url_for('add_subview_form', view_id=self.view_id),
                'form_edit': url_for('edit_subview_form', id=self.id),
                'sensor': url_for('get_sensor', id=self.sensor_id),
                'chartconfig': url_for('get_chartconfig', id=self.chartconfig_id),
                'view_id': url_for('get_view', id=self.view_id)
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['sensor_id', 'chartconfig_id', 'view_id']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        view = View.query.filter(View.id==data['view_id']).first()
        if view.is_full():
            abort(400)
        subview = Subview()
        for key in data_keys:
            setattr(subview, key, data[key])
        return subview

class View(db.Model):
    __tablename__ = 'views'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    refresh_time = db.Column(db.Integer, nullable=False)

    subviews = db.relationship('Subview', backref='view', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def icon(self):
        if self.count == 1:
            return '1x1.svg'
        elif self.count == 2:
            return '2x1.svg'
        elif self.count == 4:
            return '2x2.svg'

    def check_count(self, cnt):
        if cnt in [1, 2, 4] and self.number_of_subviews() < cnt:
            return True
        return False

    def check_refresh_time(self, rtime):
        if rtime in xrange(10, 61):
            return True
        return False

    def is_full(self):
        return self.number_of_subviews() == self.count

    def number_of_subviews(self):
        return len([subview for subview in self.subviews])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'count': self.count,
            'refresh_time': self.refresh_time,
            'links': {
                'self': url_for('get_view', id=self.id),
                'icon': url_for('static', filename='icons/'+self.icon),
                'charts_init': url_for('get_charts_skeleton', view_id=self.id),
                'charts_refresh': url_for('refresh_charts', view_id=self.id),
                'form_add': url_for('add_view_form'),
                'form_edit': url_for('edit_view_form', id=self.id),
                'subviews': [url_for('get_subview', id=subview.id) for subview in self.subviews]
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['name', 'count', 'refresh_time']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        view = View()
        if not view.check_count(data['count']) or not view.check_refresh_time(data['refresh_time']):
            abort(400)
        for key in data_keys:
            setattr(view, key, data[key])
        return view

# queries

def all_categories():
    return Category.query

def resolve_category_ids(category_ids):
    return [categ.to_dict() for categ in all_categories().filter(Category.id.in_(category_ids)).all()]

def all_sensors():
    return Sensor.query.join(Category, Sensor.category_id==Category.id)

def sensors_by_category(category_name):
    return all_sensors().filter(Category.name==category_name)

def all_datas():
    return Data.query.join(Sensor, Data.sensor_id==Sensor.id)

def datas_by_sensor(sensor_name):
    return all_datas().filter(Sensor.name==sensor_name)

def all_subviews():
    return Subview.query

def all_views():
    return View.query

def all_chartconfigs():
    return ChartConfig.query

def create_chartconfigs():
    for chart_type in chartjs.chart_types:
        chart_config = ChartConfig(type=chart_type)
        db.session.add(chart_config)
        db.session.commit()

# forms

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(min=4, max=20)])
    min_value = IntegerField('Minimum value', validators=[Required()])
    max_value = IntegerField('Maximum value', validators=[Required()])

class SensorForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(min=4, max=20)])
    category_name = StringField('Category', validators=[Required(), Length(min=4, max=20)])
    location = StringField('Location', validators=[Optional(), Length(min=3, max=40)])
    ipv4_addr = StringField('IPv4 address', validators=[Optional(), IPAddress()])

    def populate_obj(self, sen):
        sen.name = self.name.data
        sen.location = self.location.data
        sen.ipv4_addr = self.ipv4_addr.data
        sen.category_id = all_categories().filter(Category.name==self.category_name.data).first().id

class SubviewForm(FlaskForm):
    view_id = HiddenField('View')
    sensor_name = QuerySelectField('Sensor', \
        query_factory=lambda: all_sensors().order_by(Sensor.id).all(), \
        allow_blank=True, blank_text='Select a category')
    chartconfig_type = QuerySelectField('Chart type', \
        query_factory=lambda: all_chartconfigs().order_by(ChartConfig.id).all(), \
        allow_blank=True, blank_text='Select a chart type')

    def populate_obj(self, subview):
        subview.view_id = self.view_id.data
        subview.sensor_id = all_sensors().filter(Sensor.name==self.sensor_name.data.__str__()).first().id
        subview.chartconfig_id = all_chartconfigs().filter(ChartConfig.type==self.chartconfig_type.data.__str__()).first().id

class ViewForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(min=4, max=20)])
    count = IntegerField('Count', validators=[Required(), AnyOf(values=[1, 2, 4])])
    refresh_time = IntegerField('Refresh time', validators=[Required(), NumberRange(min=10, max=60)])

# routes

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html.j2')

@app.route('/<username>', methods=['GET'])
def userpage(username):
    return render_template('userpage.html.j2', username=username)

@app.route('/forms/categories/add', methods=['GET', 'POST'])
def add_category_form():
    form = CategoryForm()
    if form.validate_on_submit():
        categ = Category()
        form.populate_obj(categ)
        db.session.add(categ)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('userpage', username='user'))   # TODO change 'user' everywhere
    return render_template('form.html.j2', title='Add category', url=url_for('add_category_form'), form=form, cta='Add')

@app.route('/forms/categories/edit/<id>', methods=['GET', 'POST'])
def edit_category_form(id):
    categ = all_categories().filter(Category.id==id).first()
    form = CategoryForm(obj=categ)
    if form.validate_on_submit():
        form.populate_obj(categ)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('userpage', username='user'))
    return render_template('form.html.j2', title='Edit category', url=url_for('edit_category_form', id=id), form=form, cta='Edit')

@app.route('/forms/sensors/add', methods=['GET', 'POST'])
def add_sensor_form():
    form = SensorForm()
    if form.validate_on_submit():
        sen = Sensor()
        form.populate_obj(sen)
        db.session.add(sen)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('userpage', username='user'))
    return render_template('form.html.j2', title='Add sensor', url=url_for('add_sensor_form'), form=form, cta='Add')

@app.route('/forms/sensors/edit/<id>', methods=['GET', 'POST'])
def edit_sensor_form(id):
    sen = all_sensors().filter(Sensor.id==id).first()
    form = SensorForm(obj=sen)

    if form.validate_on_submit():
        form.populate_obj(sen)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('userpage', username='user'))

    categ = all_categories().filter(Category.id==sen.category_id).first()
    form.category_name.data = categ.name

    return render_template('form.html.j2', title='Edit sensor', url=url_for('edit_sensor_form', id=id), form=form, cta='Edit')

@app.route('/forms/subviews/add/<view_id>', methods=['GET', 'POST'])
def add_subview_form(view_id):
    form = SubviewForm()
    if form.validate_on_submit():
        subview = Subview()
        form.populate_obj(subview)
        db.session.add(subview)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('userpage', username='user'))
    form.view_id.data = view_id
    return render_template('form.html.j2', title='Add subview', url=url_for('add_subview_form', view_id=view_id), form=form, cta='Add')

@app.route('/forms/subviews/edit/<id>', methods=['GET', 'POST'])
def edit_subview_form(id):
    subview = all_subviews().filter(Subview.id==id).first()
    form = SubviewForm(obj=subview)

    if form.validate_on_submit():
        form.populate_obj(subview)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('userpage', username='user'))

    form.sensor_name.data = all_sensors().filter(Sensor.id==subview.sensor_id).first()
    form.chartconfig_type.data = all_chartconfigs().filter(ChartConfig.id==subview.chartconfig_id).first()

    return render_template('form.html.j2', title='Edit subview', url=url_for('edit_subview_form', id=id), form=form, cta='Edit')

@app.route('/forms/views/add', methods=['GET', 'POST'])
def add_view_form():
    form = ViewForm()
    if form.validate_on_submit():
        view = View()
        form.populate_obj(view)
        db.session.add(view)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('userpage', username='user'))
    return render_template('form.html.j2', title='Add view', url=url_for('add_view_form'), form=form, cta='Add')

@app.route('/forms/views/edit/<id>', methods=['GET', 'POST'])
def edit_view_form(id):
    view = all_views().filter(View.id==id).first()
    form = ViewForm(obj=view)

    if form.validate_on_submit():
        form.populate_obj(view)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('userpage', username='user'))

    return render_template('form.html.j2', title='Edit view', url=url_for('edit_view_form', id=id), form=form, cta='Edit')

@app.route('/charts/<view_id>', methods=['GET'])
def get_charts_skeleton(view_id):
    view = all_views().filter(View.id==view_id).first()
    if view is None:
        abort(400)
    number_of_subviews = view.number_of_subviews();
    width = 1200 if number_of_subviews != 4 else 550
    height = 300 if number_of_subviews != 1 else 600
    charts = []
    for subview in view.subviews:
        category = all_categories().filter(Category.id==all_sensors().filter(Sensor.id==subview.sensor_id).first().category_id).first()
        chartconfig = all_chartconfigs().filter(ChartConfig.id==subview.chartconfig_id).first()
        canvas = chartjs.Canvas('chart{0}'.format(subview.id), width, height)
        options = chartjs.Options(float(category.min_value), float(category.max_value))
        chart_builder = chartjs.ChartBuilder(chartconfig.type, options)
        chart = chartjs.Chart(canvas, 'ctx{0}'.format(subview.id), chart_builder)
        chart_builder.create_dataset(category.name)
        charts.append(chart.to_dict())
    return render_template('charts.html.j2', charts=charts)

@app.route('/charts/<view_id>/refresh', methods=['GET'])
def refresh_charts(view_id):
    view = all_views().filter(View.id==view_id).first()
    if view is None or len(request.args) != view.number_of_subviews():
        abort(400)
    refresh_data = {}
    for subview in view.subviews:
        last_index = int(request.args.get('chart{0}'.format(subview.id)))
        datas_since_index = all_sensors().filter(Sensor.id==subview.sensor_id).first().datas[last_index:]
        refresh_data['chart{0}'.format(subview.id)] = [data.to_dict() for data in datas_since_index]
    return jsonify(refresh_data)

# api

@app.route('/categories', methods=['GET'])
def get_categories():
    categs = all_categories().order_by(Category.id).all()
    return jsonify({'categories': [categ.to_dict() for categ in categs]})

@app.route('/category', methods=['POST'])
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
    resp.headers['Location'] = url_for('get_category', id=categ.id)
    return resp

@app.route('/category/<id>', methods=['GET'])
def get_category(id):
    categ = all_categories().filter(Category.id==id).first()
    if categ is None:
        abort(400)
    return jsonify(categ.to_dict())

@app.route('/category/<id>', methods=['DELETE'])
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

@app.route('/category/<id>', methods=['PUT'])
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

@app.route('/sensors', methods=['GET'])
def get_sensors():
    sens = all_sensors().order_by(Sensor.id).all()
    return jsonify({'sensors': [sen.to_dict() for sen in sens]})

@app.route('/sensor', methods=['POST'])
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
    resp.headers['Location'] = url_for('get_sensor', id=sen.id)
    return resp

@app.route('/sensor/<id>', methods=['GET'])
def get_sensor(id):
    sen = all_sensors().filter(Sensor.id==id).first()
    if sen is None:
        abort(400)
    return jsonify(sen.to_dict())

@app.route('/sensor/<id>', methods=['DELETE'])
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
    resp = jsonify('')
    resp.status_code = 204
    return resp

@app.route('/sensor/<id>', methods=['PUT'])
def modify_sensor(id):
    sen = all_sensors().filter(Sensor.id==id).first()
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

@app.route('/data', methods=['POST'])
def add_data():
    dat = Data.from_dict(json.loads(request.data))
    db.session.add(dat)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    sensor_name = all_sensors().filter(Sensor.id==dat.sensor_id).first().name
    resp = jsonify(dat.to_dict())
    resp.status_code = 201
    resp.headers['Location'] = url_for('get_data', id=dat.id)
    return resp

@app.route('/data/<id>', methods=['GET'])
def get_data(id):
    dat = all_datas().filter(Data.id==id).first()
    if dat is None:
        abort(400)
    return jsonify(dat.to_dict())

@app.route('/chartconfigs', methods=['GET'])
def get_chartconfigs():
    chartconfigs = all_chartconfigs().order_by(ChartConfig.id).all()
    return jsonify({'chartconfigs': [chartconfig.to_dict() for chartconfig in chartconfigs]})

@app.route('/chartconfig/<id>', methods=['GET'])
def get_chartconfig(id):
    chartconfig = all_chartconfigs().filter(ChartConfig.id==id).first()
    if chartconfig is None:
        abort(400)
    return jsonify(chartconfig.to_dict())

@app.route('/subview/<id>', methods=['GET'])
def get_subview(id):
    subview = all_subviews().filter(Subview.id==id).first()
    if subview is None:
        abort(400)
    return jsonify(subview.to_dict())

@app.route('/subview', methods=['POST'])
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
    resp.headers['Location'] = url_for('get_subview', id=subview.id)
    return resp

@app.route('/subview/<id>', methods=['PUT'])
def modify_subview(id):
    subview = all_subviews().filter(Subview.id==id).first()
    request_data = json.loads(request.data)
    if 'view_id' in request_data.iterkeys():
        view = all_views().filter(View.id==id).first()
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

@app.route('/subview/<id>', methods=['DELETE'])
def remove_subview(id):
    subview = all_subviews().filter(Subview.id==id).first()
    if subview is None:
        abort(400)
    db.session.delete(subview)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify('')
    resp.status_code = 204
    return resp

@app.route('/views', methods=['GET'])
def get_views():
    views = all_views().order_by(View.id).all()
    return jsonify({'views': [view.to_dict() for view in views]})

@app.route('/view/<id>', methods=['GET'])
def get_view(id):
    view = all_views().filter(View.id==id).first()
    if view is None:
        abort(400)
    return jsonify(view.to_dict())

@app.route('/view', methods=['POST'])
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
    resp.headers['Location'] = url_for('get_view', id=view.id)
    return resp

@app.route('/view/<id>', methods=['PUT'])
def modify_view(id):
    view = all_views().filter(View.id==id).first()
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

@app.route('/view/<id>', methods=['DELETE'])
def remove_view(id):
    view = all_views().filter(View.id==id).first()
    if view is None:
        abort(400)
    db.session.delete(view)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400)
    resp = jsonify('')
    resp.status_code = 204
    return resp

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    create_chartconfigs()
    app.run(debug=True)
