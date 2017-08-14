from flask import Blueprint, render_template, redirect, url_for, jsonify, abort, flash, current_app
from flask_login import login_user, current_user, login_required
from sqlalchemy.exc import IntegrityError

from .. import db
from ..models import Category, Sensor, Subview, View, ChartConfig, User
from ..queries import all_categories, all_sensors, all_subviews, all_views, all_chartconfigs, all_users
from ..forms import CategoryForm, SensorForm, SubviewForm, ViewForm, UserForm, LoginForm
from ..utils import send_email
from ..decorators import check_confirmed

forms = Blueprint('forms', __name__)

@forms.route('/forms/login', methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    if form.validate_on_submit():
        user = all_users().filter(User.username==form.username.data).first()
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
    user = all_users().filter(User.id==current_user.id).first()
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
        categ = Category()
        form.populate_obj(categ)
        db.session.add(categ)
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
    categ = all_categories().filter(Category.id==id).first()
    form = CategoryForm(obj=categ)
    if form.validate_on_submit():
        form.populate_obj(categ)
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
    sen = all_sensors().filter(Sensor.id==id).first()
    form = SensorForm(obj=sen)

    if form.validate_on_submit():
        form.populate_obj(sen)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))

    categ = all_categories().filter(Category.id==sen.category_id).first()
    form.category_name.data = categ.name

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
    subview = all_subviews().filter(Subview.id==id).first()
    form = SubviewForm(obj=subview)

    if form.validate_on_submit():
        form.populate_obj(subview)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))

    form.sensor_name.data = all_sensors().filter(Sensor.id==subview.sensor_id).first()
    form.chartconfig_type.data = all_chartconfigs().filter(ChartConfig.id==subview.chartconfig_id).first()

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
    view = all_views().filter(View.id==id).first()
    form = ViewForm(obj=view)

    if form.validate_on_submit():
        form.populate_obj(view)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))

    return render_template('form.html.j2', title='Edit view', url=url_for('forms.edit_view_form', id=id), form=form, cta='Edit')
