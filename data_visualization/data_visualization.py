import json

from flask import render_template, redirect, url_for, request, jsonify, abort, session, Blueprint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only

import chartjs

from .models import *
from .queries import *
from .forms import *

# routes

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html.j2')

@main.route('/<username>', methods=['GET'])
def userpage(username):
    return render_template('userpage.html.j2', username=username)

forms = Blueprint('forms', __name__)

@forms.route('/forms/categories/add', methods=['GET', 'POST'])
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
        return redirect(url_for('main.userpage', username='user'))   # TODO change 'user' everywhere
    return render_template('form.html.j2', title='Add category', url=url_for('forms.add_category_form'), form=form, cta='Add')

@forms.route('/forms/categories/edit/<id>', methods=['GET', 'POST'])
def edit_category_form(id):
    categ = all_categories().filter(Category.id==id).first()
    form = CategoryForm(obj=categ)
    if form.validate_on_submit():
        form.populate_obj(categ)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', username='user'))
    return render_template('form.html.j2', title='Edit category', url=url_for('forms.edit_category_form', id=id), form=form, cta='Edit')

@forms.route('/forms/sensors/add', methods=['GET', 'POST'])
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
        return redirect(url_for('main.userpage', username='user'))
    return render_template('form.html.j2', title='Add sensor', url=url_for('forms.add_sensor_form'), form=form, cta='Add')

@forms.route('/forms/sensors/edit/<id>', methods=['GET', 'POST'])
def edit_sensor_form(id):
    sen = all_sensors().filter(Sensor.id==id).first()
    form = SensorForm(obj=sen)

    if form.validate_on_submit():
        form.populate_obj(sen)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', username='user'))

    categ = all_categories().filter(Category.id==sen.category_id).first()
    form.category_name.data = categ.name

    return render_template('form.html.j2', title='Edit sensor', url=url_for('forms.edit_sensor_form', id=id), form=form, cta='Edit')

@forms.route('/forms/subviews/add/<view_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.userpage', username='user'))
    form.view_id.data = view_id
    return render_template('form.html.j2', title='Add subview', url=url_for('forms.add_subview_form', view_id=view_id), form=form, cta='Add')

@forms.route('/forms/subviews/edit/<id>', methods=['GET', 'POST'])
def edit_subview_form(id):
    subview = all_subviews().filter(Subview.id==id).first()
    form = SubviewForm(obj=subview)

    if form.validate_on_submit():
        form.populate_obj(subview)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', username='user'))

    form.sensor_name.data = all_sensors().filter(Sensor.id==subview.sensor_id).first()
    form.chartconfig_type.data = all_chartconfigs().filter(ChartConfig.id==subview.chartconfig_id).first()

    return render_template('form.html.j2', title='Edit subview', url=url_for('forms.edit_subview_form', id=id), form=form, cta='Edit')

@forms.route('/forms/views/add', methods=['GET', 'POST'])
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
        return redirect(url_for('main.userpage', username='user'))
    return render_template('form.html.j2', title='Add view', url=url_for('forms.add_view_form'), form=form, cta='Add')

@forms.route('/forms/views/edit/<id>', methods=['GET', 'POST'])
def edit_view_form(id):
    view = all_views().filter(View.id==id).first()
    form = ViewForm(obj=view)

    if form.validate_on_submit():
        form.populate_obj(view)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', username='user'))

    return render_template('form.html.j2', title='Edit view', url=url_for('forms.edit_view_form', id=id), form=form, cta='Edit')

# api

api = Blueprint('api', __name__)

@api.route('/charts/<view_id>', methods=['GET'])
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

@api.route('/charts/<view_id>/refresh', methods=['GET'])
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
    resp = jsonify('')
    resp.status_code = 204
    return resp

@api.route('/sensor/<id>', methods=['PUT'])
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

@api.route('/data', methods=['POST'])
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
    resp.headers['Location'] = url_for('api.get_data', id=dat.id)
    return resp

@api.route('/data/<id>', methods=['GET'])
def get_data(id):
    dat = all_datas().filter(Data.id==id).first()
    if dat is None:
        abort(400)
    return jsonify(dat.to_dict())

@api.route('/chartconfigs', methods=['GET'])
def get_chartconfigs():
    chartconfigs = all_chartconfigs().order_by(ChartConfig.id).all()
    return jsonify({'chartconfigs': [chartconfig.to_dict() for chartconfig in chartconfigs]})

@api.route('/chartconfig/<id>', methods=['GET'])
def get_chartconfig(id):
    chartconfig = all_chartconfigs().filter(ChartConfig.id==id).first()
    if chartconfig is None:
        abort(400)
    return jsonify(chartconfig.to_dict())

@api.route('/subview/<id>', methods=['GET'])
def get_subview(id):
    subview = all_subviews().filter(Subview.id==id).first()
    if subview is None:
        abort(400)
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

@api.route('/subview/<id>', methods=['DELETE'])
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

@api.route('/views', methods=['GET'])
def get_views():
    views = all_views().order_by(View.id).all()
    return jsonify({'views': [view.to_dict() for view in views]})

@api.route('/view/<id>', methods=['GET'])
def get_view(id):
    view = all_views().filter(View.id==id).first()
    if view is None:
        abort(400)
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

@api.route('/view/<id>', methods=['DELETE'])
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
