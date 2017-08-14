from flask import current_app
from flask_mail import Message

from . import mail
from .decorators import async

@async
def send_email_async(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, body):
    msg = Message(subject=subject, html=body, recipients=[to])
    send_email_async(app=current_app._get_current_object(), msg=msg)
