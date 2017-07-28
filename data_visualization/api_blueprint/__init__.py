from flask import Blueprint

api = Blueprint('api', __name__)

from . import charts, categories, sensors, datas, chartconfigs, subviews, views
