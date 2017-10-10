import os
import json

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

def find_tests_by_names(testsuite_all, *args):
    tests = []
    for arg in args:
        tests.append(find_test_by_name(testsuite_all, arg))
    return tests

def find_test_by_name(testsuite_all, test_name):
    def _find_test_by_name(testsuite, name):
        for _test in getattr(testsuite, '_tests'):
            if hasattr(_test, '_tests'):
                result = _find_test_by_name(_test, name)
                if result:
                    return result
            else:
                method, classpath = _test.__str__().split(' ')
                if method.lstrip('test_') == name:
                    result = 'tests.' + classpath.strip('()') + '.' + method
                    return result
        return None

    result = None
    for testsuite in testsuite_all:
        result = _find_test_by_name(testsuite, test_name)
        if result:
            return result
    return None
