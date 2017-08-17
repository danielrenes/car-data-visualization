from flask import Blueprint, render_template, redirect, url_for, jsonify, abort, flash, current_app
from flask_login import login_user, current_user, login_required
from sqlalchemy.exc import IntegrityError

from .. import db
from ..models import Category, Sensor, Subview, View, ChartConfig, User
from ..queries import query_get_category_by_id, query_get_sensor_by_id, query_get_subview_by_id, query_get_view_by_id, \
    query_get_user_by_id, query_get_user_by_name, query_get_chartconfig_by_id
from ..forms import CategoryForm, SensorForm, SubviewForm, ViewForm, UserForm, LoginForm
from ..utils import send_email
from ..decorators import check_confirmed

forms = Blueprint('forms', __name__)

@forms.route('/forms/login', methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    if form.validate_on_submit():
        user = query_get_user_by_name(form.username.data)
        if user is None:
            abort(400)
        if not user.confirmed:
            flash('Please activate your account!', 'warning')
            return redirect(url_for('main.index'))
        if user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.userpage', user_slug=user.user_slug))
    return render_template('form.html.j2', title='Login', url=url_for('forms.login_form'), form=form, cta='Login')

@forms.route('/forms/users/add', methods=['GET', 'POST'])
def add_user_form():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        try:
            db.session.commit()
            token = user.generate_confirmation_token()
            url = url_for('main.confirm_email', token=token, _external=True)
            send_email(to=user.email, subject='Confirm Your Account', body=render_template('activate.html.j2', url=url))
        except IntegrityError:
            db.session.rollback()
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('form.html.j2', title='Sign Up', url=url_for('forms.add_user_form'), form=form, cta='Sign Up')

@forms.route('/forms/users/edit', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_user_form():
    user = query_get_user_by_id(current_user.id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=user.user_slug))
    form.password.data = None
    form.repeat_password.data = None
    return render_template('form.html.j2', title='Edit profile', url=url_for('forms.edit_user_form', id=id), form=form, cta='Save')

@forms.route('/forms/categories/add/<user_id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def add_category_form(user_id):
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category()
        form.populate_obj(category)
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))
    form.user_id.data = user_id
    return render_template('form.html.j2', title='Add category', url=url_for('forms.add_category_form', user_id=user_id), form=form, cta='Add')

@forms.route('/forms/categories/edit/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_category_form(id):
    category = query_get_category_by_id(id, current_user.id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))
    return render_template('form.html.j2', title='Edit category', url=url_for('forms.edit_category_form', id=id), form=form, cta='Edit')

@forms.route('/forms/sensors/add', methods=['GET', 'POST'])
@login_required
@check_confirmed
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
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))
    return render_template('form.html.j2', title='Add sensor', url=url_for('forms.add_sensor_form'), form=form, cta='Add')

@forms.route('/forms/sensors/edit/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_sensor_form(id):
    sensor = query_get_sensor_by_id(id, current_user.id)
    form = SensorForm(obj=sensor)

    if form.validate_on_submit():
        form.populate_obj(sensor)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))

    category = query_get_category_by_id(sensor.category_id, current_user.id)
    form.category_name.data = category.name

    return render_template('form.html.j2', title='Edit sensor', url=url_for('forms.edit_sensor_form', id=id), form=form, cta='Edit')

@forms.route('/forms/subviews/add/<view_id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
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
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))
    form.view_id.data = view_id
    return render_template('form.html.j2', title='Add subview', url=url_for('forms.add_subview_form', view_id=view_id), form=form, cta='Add')

@forms.route('/forms/subviews/edit/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_subview_form(id):
    subview = query_get_subview_by_id(id)
    form = SubviewForm(obj=subview)

    if form.validate_on_submit():
        form.populate_obj(subview)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))

    form.sensor_name.data = query_get_sensor_by_id(subview.sensor_id, current_user.id)
    form.chartconfig_type.data = query_get_chartconfig_by_id(subview.chartconfig_id)

    return render_template('form.html.j2', title='Edit subview', url=url_for('forms.edit_subview_form', id=id), form=form, cta='Edit')

@forms.route('/forms/views/add', methods=['GET', 'POST'])
@login_required
@check_confirmed
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
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))
    return render_template('form.html.j2', title='Add view', url=url_for('forms.add_view_form'), form=form, cta='Add')

@forms.route('/forms/views/edit/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_view_form(id):
    view = query_get_view_by_id(id, current_user.id)
    form = ViewForm(obj=view)

    if form.validate_on_submit():
        form.populate_obj(view)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))

    return render_template('form.html.j2', title='Edit view', url=url_for('forms.edit_view_form', id=id), form=form, cta='Edit')
