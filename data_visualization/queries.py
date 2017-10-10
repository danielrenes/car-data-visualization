from .models import Category, Sensor, Data, Subview, View, ChartConfig, User, PredefinedConfiguration, PreconfiguredView
from .decorators import success_or_abort

@success_or_abort
def query_all_categories(user_id):
    return Category.query.join(User, User.id==Category.user_id).filter(User.id==user_id).order_by(Category.id).all()

@success_or_abort
def query_get_category_by_id(id, user_id):
    return Category.query.join(User, User.id==Category.user_id).filter(User.id==user_id, Category.id==id).first()

@success_or_abort
def query_get_category_by_name(name, user_id):
    return Category.query.join(User, User.id==Category.user_id).filter(User.id==user_id, Category.name==name).first()

@success_or_abort
def query_all_sensors(user_id):
    return Sensor.query.join(Category, Sensor.category_id==Category.id).join(User, User.id==Category.user_id)\
        .filter(User.id==user_id).order_by(Sensor.id).all()

@success_or_abort
def query_get_sensor_by_id(id, user_id):
    return Sensor.query.join(Category, Sensor.category_id==Category.id).join(User, User.id==Category.user_id)\
        .filter(User.id==user_id, Sensor.id==id).first()

@success_or_abort
def query_get_sensor_by_name(name, user_id):
    return Sensor.query.join(Category, Sensor.category_id==Category.id).join(User, User.id==Category.user_id)\
        .filter(User.id==user_id, Sensor.name==name).first()

@success_or_abort
def query_all_datas(user_id):
    return Data.query.join(Sensor, Data.sensor_id==Sensor.id).join(Category, Sensor.category_id==Category.id)\
        .join(User, User.id==Category.user_id).filter(User.id==user_id).order_by(Data.id).all()

@success_or_abort
def query_get_data_by_id(id, user_id):
    return Data.query.join(Sensor, Data.sensor_id==Sensor.id).join(Category, Sensor.category_id==Category.id)\
        .join(User, User.id==Category.user_id).filter(User.id==user_id, Data.id==id).first()

@success_or_abort
def query_all_subviews(user_id):
    return Subview.query.join(Sensor, Subview.sensor_id==Sensor.id).join(Category, Sensor.category_id==Category.id)\
        .join(User, User.id==Category.user_id).filter(User.id==user_id).order_by(Subview.id).all()

@success_or_abort
def query_get_subview_by_id(id, user_id):
    return Subview.query.join(Sensor, Subview.sensor_id==Sensor.id).join(Category, Sensor.category_id==Category.id)\
        .join(User, User.id==Category.user_id).filter(User.id==user_id, Subview.id==id).first()

@success_or_abort
def query_all_views(user_id):
    all_views = []
    all_views.extend(View.query.join(User, User.id==View.user_id).filter(User.id==user_id).order_by(View.id).all())
    all_views.extend(PreconfiguredView.query.join(User, User.id==PreconfiguredView.user_id).filter(User.id==user_id).order_by(PreconfiguredView.id).all())
    return all_views

@success_or_abort
def query_get_view_by_id(id, user_id):
    view = View.query.join(User, User.id==View.user_id).filter(User.id==user_id, View.id==id).first()
    if view:
        return view
    else:
        view = PreconfiguredView.query.join(User, User.id==PreconfiguredView.user_id).filter(User.id==user_id, PreconfiguredView.id==id).first()
        return view

@success_or_abort
def query_get_user_by_id(id):
    return User.query.filter(User.id==id).first()

@success_or_abort
def query_get_user_by_name(username):
    return User.query.filter(User.username==username).first()

@success_or_abort
def query_all_chartconfigs():
    return ChartConfig.query.order_by(ChartConfig.id).all()

@success_or_abort
def query_get_chartconfig_by_id(id):
    return ChartConfig.query.filter(ChartConfig.id==id).first()

@success_or_abort
def query_get_chartconfig_by_type(type):
    return ChartConfig.query.filter(ChartConfig.type==type).first()

@success_or_abort
def query_all_predefined_configs():
    return PredefinedConfiguration.query.order_by(PredefinedConfiguration.id).all()

# TODO:  modify so the user can only access their own predefined config
@success_or_abort
def query_get_predefined_config_by_id(id):
    return PredefinedConfiguration.query.filter(PredefinedConfiguration.id==id).first()
