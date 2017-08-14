from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField, PasswordField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional, Length, IPAddress, NumberRange, AnyOf, Email, EqualTo

from .models import Category, Sensor, ChartConfig
from .queries import all_categories, all_sensors, all_chartconfigs

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Required(), Length(min=8, max=32)])
    password = PasswordField('Password', validators=[Required()])

class UserForm(FlaskForm):
    username = StringField('Username', validators=[Required(), Length(min=8, max=32)])
    email = StringField('Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required(), EqualTo('repeat_password')])
    repeat_password = PasswordField('Repeat password')

    def populate_obj(self, user):
        user.username = self.username.data
        user.email = self.email.data
        user.password = self.password.data

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(min=4, max=20)])
    min_value = IntegerField('Minimum value', validators=[Required()])
    max_value = IntegerField('Maximum value', validators=[Required()])
    user_id = HiddenField('User')

class SensorForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(min=4, max=20)])
    category_name = StringField('Category', validators=[Required(), Length(min=4, max=20)])
    location = StringField('Location', validators=[Optional(), Length(min=3, max=40)])
    ipv4_addr = StringField('IPv4 address', validators=[Optional(), IPAddress()])

    def populate_obj(self, sen):
        sen.name = self.name.data
        sen.location = self.location.data
        sen.ipv4_addr = self.ipv4_addr.data
        sen.category_id = all_categories().filter(Category.name==self.category_name.data).first().id

class SubviewForm(FlaskForm):
    view_id = HiddenField('View')
    sensor_name = QuerySelectField('Sensor', \
        query_factory=lambda: all_sensors().order_by(Sensor.id).all(), \
        allow_blank=True, blank_text='Select a sensor')
    chartconfig_type = QuerySelectField('Chart type', \
        query_factory=lambda: all_chartconfigs().order_by(ChartConfig.id).all(), \
        allow_blank=True, blank_text='Select a chart type')

    def populate_obj(self, subview):
        subview.view_id = self.view_id.data
        subview.sensor_id = all_sensors().filter(Sensor.name==self.sensor_name.data.__str__()).first().id
        subview.chartconfig_id = all_chartconfigs().filter(ChartConfig.type==self.chartconfig_type.data.__str__()).first().id

class ViewForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(min=4, max=20)])
    count = IntegerField('Count', validators=[Required(), AnyOf(values=[1, 2, 4])])
    refresh_time = IntegerField('Refresh time', validators=[Required(), NumberRange(min=10, max=60)])
