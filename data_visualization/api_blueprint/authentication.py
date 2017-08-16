from flask import g, jsonify, redirect, url_for, flash, current_app
from flask_httpauth import HTTPBasicAuth

from . import api
from ..models import User

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    if password == '':
        token = username_or_token
        g.current_user = User.verify_auth_token(token)
        g.token_used = True
        return g.current_user is not None
    else:
        username = username_or_token
        user = User.query.filter(User.username==username).first()
        if user is None:
            return False
        g.current_user = user
        g.token_used = False
        return user.verify_password(password)

@auth.error_handler
def auth_error():
    flash('Unauthorized', 'error')
    return redirect(url_for('main.index'))

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.confirmed:
        return '', 403

@api.route('/token', methods=['GET'])
def get_token():
    import os
    if g.token_used:
        return '', 403
    expiration = 20 if current_app.config['TESTING'] == True else 600
    return jsonify({'token': g.current_user.generate_auth_token(expiration=expiration), 'expiration': expiration})
