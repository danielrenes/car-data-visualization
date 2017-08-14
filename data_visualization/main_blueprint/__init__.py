from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required, logout_user

from ..forms_blueprint import login_form, add_user_form
from ..decorators import check_confirmed

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    if getattr(current_user, 'confirmed', False):
        return redirect(url_for('main.userpage', user_slug=current_user.user_slug))
    return render_template('index.html.j2', login_form=login_form(), signup_form=add_user_form())

@main.route('/<user_slug>', methods=['GET'])
@login_required
@check_confirmed
def userpage(user_slug):
    if current_user.user_slug == user_slug:
        return render_template('userpage.html.j2', username=current_user.username)
    return redirect(url_for('main.index'))

@main.route('/confirm/<token>', methods=['GET'])
@login_required
def confirm_email(token):
    if getattr(current_user, 'confirmed', False):
        return redirct(url_for('main.userpage', user_slug=current_user.user_slug))
    if current_user.confirm_email(token):
        flash('You have successfully activated your account.', 'success')
    else:
        flash('Your account activation was denied', 'error')
    return redirect(url_for('main.index'))

@main.route('/logout')
@login_required
@check_confirmed
def logout():
    logout_user()
    return redirect(url_for('main.index'))
