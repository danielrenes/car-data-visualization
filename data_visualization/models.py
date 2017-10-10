import datetime
from flask import url_for, abort, current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from . import db

def check_keys(legal_keys, keys):
    if len(keys) > len(legal_keys):
        abort(400)
    found_keys = []
    for key in keys:
        if key not in legal_keys:
            abort(400)
        if key in found_keys:
            abort(400)
        found_keys.append(key)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    token_used = db.Column(db.Boolean, default=False)

    categories = db.relationship('Category', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    views = db.relationship('View', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def password(self):
        pass

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return serializer.dumps({'confirm': self.id})

    def generate_auth_token(self, expiration=600):
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return serializer.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except:
            return None
        if not data.get('id', None):
            return None
        user = User.query.get_or_404(data['id'])
        return user

    def confirm_email(self, token):
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return False
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'links': {
                'self': url_for('api.get_user'),
                'form_edit': url_for('forms.edit_user_form'),
                'categories': [url_for('api.get_category', id=categ.id) for categ in self.categories],
                'views': [url_for('api.get_view', id=view.id) for view in self.views],
                '_fallback': {
                    'categories': {
                        'form_add': url_for('forms.add_category_form', user_id=self.id),
                    },
                    'sensors': {
                        'form_add': url_for('forms.add_sensor_form'),
                    },
                    'views': {
                        'form_add': url_for('forms.add_view_form')
                    }
                }
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['username', 'email', 'password']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        user = User()
        for key in data_keys:
            setattr(user, key, data[key])
        return user

    @property
    def user_slug(self):
        return self.username.replace(' ', '.')

    @staticmethod
    def generate_fake_user(username, email, password):
        if current_app.config['DEBUG']:
            fake_user = User(username=username, email=email, password=password, confirmed=True)
            db.session.add(fake_user)
            try:
                db.session.commit()
            except:
                db.session.rollback()

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20), unique=True, nullable=False)
    min_value = db.Column(db.Integer, nullable=False)
    max_value = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(8), default='')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    sensors = db.relationship('Sensor', backref='category', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'unit': self.unit,
            'links': {
                'self': url_for('api.get_category', id=self.id),
                'form_add': url_for('forms.add_category_form', user_id=self.user_id),
                'form_edit': url_for('forms.edit_category_form', id=self.id),
                'sensors': [url_for('api.get_sensor', id=sensor.id) for sensor in self.sensors]
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['name', 'min_value', 'max_value', 'unit', 'user_id']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        categ = Category()
        for key in data_keys:
            setattr(categ, key, data[key])
        return categ

class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20), unique=True, nullable=False)
    location = db.Column(db.String(40))
    ipv4_addr = db.Column(db.String(15), unique=True)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    datas = db.relationship('Data', backref='sensor', lazy='dynamic', cascade='all, delete-orphan')
    subviews = db.relationship('Subview', backref='sensor', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'location': self.location,
            'ipv4_addr': self.ipv4_addr,
            'links': {
                'self': url_for('api.get_sensor', id=self.id),
                'form_add': url_for('forms.add_sensor_form'),
                'form_edit': url_for('forms.edit_sensor_form', id=self.id),
                'category': url_for('api.get_category', id=self.category_id),
                'datas': [url_for('api.get_data', id=data.id) for data in self.datas],
                'subviews': [url_for('api.get_subview', id=subview.id) for subview in self.subviews]
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['name', 'category_id', 'location', 'ipv4_addr']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        sen = Sensor()
        for key in data_keys:
            setattr(sen, key, data[key])
        return sen

    def __str__(self):
        return self.name

class Data(db.Model):
    __tablename__ = 'datas'

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'timestamp': self.timestamp,
            'sensor_id': self.sensor_id,
            'links': {
                'self': url_for('api.get_data', id=self.id),
                'sensor': url_for('api.get_sensor', id=self.sensor_id)
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['value', 'sensor_id']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        dat = Data()
        for key in data_keys:
            setattr(dat, key, data[key])
        return dat

class ChartConfig(db.Model):
    __tablename__ = 'chartconfigs'

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(20), nullable=False)

    subviews = db.relationship('Subview', backref='chartconfig', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'links': {
                'self': url_for('api.get_chartconfig', id=self.id),
                'subviews': [url_for('api.get_subview', id=subview.id) for subview in self.subviews]
            }
        }

    def __str__(self):
        return self.type

class Subview(db.Model):
    __tablename__ = 'subviews'

    id = db.Column(db.Integer, primary_key=True)

    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)
    chartconfig_id = db.Column(db.Integer, db.ForeignKey('chartconfigs.id'), nullable=False)
    view_id = db.Column(db.Integer, db.ForeignKey('views.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'chartconfig_id': self.chartconfig_id,
            'view_id': self.view_id,
            'links': {
                'self': url_for('api.get_subview', id=self.id),
                'form_add': url_for('forms.add_subview_form', view_id=self.view_id),
                'form_edit': url_for('forms.edit_subview_form', id=self.id),
                'sensor': url_for('api.get_sensor', id=self.sensor_id),
                'chartconfig': url_for('api.get_chartconfig', id=self.chartconfig_id),
                'view_id': url_for('api.get_view', id=self.view_id)
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['sensor_id', 'chartconfig_id', 'view_id']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        view = View.query.filter(View.id==data['view_id']).first()
        if view.is_full():
            abort(400)
        subview = Subview()
        for key in data_keys:
            setattr(subview, key, data[key])
        return subview

view_types = {
    'normal',
    'preconfigured'
}

class View(db.Model):
    __tablename__ = 'views'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    refresh_time = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), default='normal')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    subviews = db.relationship('Subview', backref='view', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def icon(self):
        if self.count == 1:
            return '1x1.svg'
        elif self.count == 2:
            return '2x1.svg'
        elif self.count == 4:
            return '2x2.svg'

    def check_count(self, cnt):
        if cnt in [1, 2, 4] and self.number_of_subviews() < cnt:
            return True
        return False

    def check_refresh_time(self, rtime):
        if rtime in xrange(10, 61):
            return True
        return False

    def is_full(self):
        return self.number_of_subviews() == self.count

    def number_of_subviews(self):
        return len([subview for subview in self.subviews])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'count': self.count,
            'refresh_time': self.refresh_time,
            'type': self.type,
            'links': {
                'self': url_for('api.get_view', id=self.id),
                'icon': url_for('static', filename='icons/'+self.icon),
                'charts_init': url_for('api.get_charts_skeleton', view_id=self.id),
                'charts_refresh': url_for('api.refresh_charts', view_id=self.id),
                'form_add': url_for('forms.add_view_form'),
                'form_edit': url_for('forms.edit_view_form', id=self.id),
                'subviews': [url_for('api.get_subview', id=subview.id) for subview in self.subviews],
                '_fallback': {
                    'subviews': {
                        'form_add': url_for('forms.add_subview_form', view_id=self.id)
                    }
                }
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['name', 'count', 'refresh_time', 'user_id']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        view = View()
        if not view.check_count(data['count']) or not view.check_refresh_time(data['refresh_time']):
            abort(400)
        for key in data_keys:
            setattr(view, key, data[key])
        return view

class PredefinedConfiguration(db.Model):
    __tablename__ = 'predefined_configurations'

    id = db.Column(db.Integer, primary_key=True)

    configuration = db.Column(db.String(4096), nullable=False)

    preconfigured_views = db.relationship('PreconfiguredView', backref='predfinedconfiguration', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'configuration': self.configuration,
            'links': {
                'self': url_for('api.get_predefined_config', id=self.id),
                'preconfigured_views': [url_for('api.get_view', id=preconfigured_view.id) for preconfigured_view in self.preconfigured_views]
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['configuration']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        predefined_configuration = PredefinedConfiguration()
        for key in data_keys:
            setattr(predefined_configuration, key, data[key])
        return predefined_configuration

class PreconfiguredView(db.Model):
    __tablename__ = 'preconfigured_views'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20), nullable=False)
    refresh_time = db.Column(db.Integer, default=60)
    type = db.Column(db.String(20), default='preconfigured')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    predefined_configuration_id = db.Column(db.Integer, db.ForeignKey('predefined_configurations.id'), nullable=False)

    @property
    def icon(self):
        return '1x1.svg'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'refresh_time': self.refresh_time,
            'type': self.type,
            'preconfiguration_id': self.predefined_configuration_id,
            'links': {
                'self': url_for('api.get_view', id=self.id),
                'predefined_configuration': url_for('api.get_predefined_config', id=self.predefined_configuration_id),
                'icon': url_for('static', filename='icons/'+self.icon),
                'charts_init': url_for('api.get_preconfigured_skeleton', view_id=self.id),
                'charts_refresh': url_for('api.refresh_preconfigured', view_id=self.id)
            }
        }

    @staticmethod
    def from_dict(data):
        if data is None:
            abort(400)
        legal_keys = ['name', 'predefined_configuration_id', 'user_id']
        data_keys = data.keys()
        check_keys(legal_keys, data_keys)
        preconfigured_view = PreconfiguredView()
        for key in data_keys:
            setattr(preconfigured_view, key, data[key])
        return preconfigured_view

class ViewWrapper(object):
    @staticmethod
    def from_dict(data):
        if data['type'] == 'normal':
            data.pop('type')
            return View.from_dict(data)
        elif data['type'] == 'preconfigured':
            data.pop('type')
            return PreconfiguredView.from_dict(data)
        else:
            abort(400)
