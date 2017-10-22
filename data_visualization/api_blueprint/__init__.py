from flask import Blueprint
from flask_login import login_required

api = Blueprint('api', __name__)

from . import authentication, charts, categories, sensors, datas, chartconfigs, subviews, views, users, predefined_configurations, maps
