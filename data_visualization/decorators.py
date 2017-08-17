from functools import wraps
from threading import Thread

from flask import flash, redirect, url_for, abort
from flask_login import current_user

def async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        thread = Thread(target=f, args=args, kwargs=kwargs)
        thread.start()
    return wrapper

def check_confirmed(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not getattr(current_user, 'confirmed', False):
            flash('Please activate your account!', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return wrapper

def success_or_abort(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        if result is None:
            abort(400)
        return result
    return wrapper
