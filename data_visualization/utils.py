from flask import current_app
from flask_mail import Message

from . import db, mail
from .models import ChartConfig
from .decorators import async
from .chartjs import chart_types

@async
def send_email_async(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, body):
    msg = Message(subject=subject, html=body, recipients=[to])
    send_email_async(app=current_app._get_current_object(), msg=msg)

def create_chartconfigs():
    for chart_type in chart_types:
        chart_config = ChartConfig(type=chart_type)
        db.session.add(chart_config)
        db.session.commit()
