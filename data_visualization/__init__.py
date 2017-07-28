import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from . import models

def create_app(config=None):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') if 'SECRET_KEY' in os.environ else 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI') if 'DATABASE_URI' in os.environ else 'sqlite://'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True

    db.init_app(app)

    from .main_blueprint import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .forms_blueprint import forms as forms_blueprint

    app.register_blueprint(forms_blueprint)

    from .api_blueprint import api as api_blueprint

    app.register_blueprint(api_blueprint)

    return app
