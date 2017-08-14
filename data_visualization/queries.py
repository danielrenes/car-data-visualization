from . import db
from .chartjs import chart_types
from .models import Category, Sensor, Data, Subview, View, ChartConfig, User

def all_categories():
    return Category.query

def all_sensors():
    return Sensor.query.join(Category, Sensor.category_id==Category.id)

def all_datas():
    return Data.query.join(Sensor, Data.sensor_id==Sensor.id)

def all_subviews():
    return Subview.query

def all_views():
    return View.query

def all_chartconfigs():
    return ChartConfig.query

def all_users():
    return User.query

def create_chartconfigs():
    for chart_type in chart_types:
        chart_config = ChartConfig(type=chart_type)
        db.session.add(chart_config)
        db.session.commit()
