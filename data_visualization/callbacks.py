from flask import url_for, redirect, flash

from . import login_manager
from .models import User

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('Unauthorized', 'error')
    return redirect(url_for('main.index'))
