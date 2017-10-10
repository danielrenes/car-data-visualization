#!/usr/bin/env python

import os

import click

from data_visualization import create_app, db
from data_visualization.utils import create_chartconfigs

app = create_app(os.environ.get('CONFIG'))

@app.cli.command('init-db', help='Create a fresh database.')
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_chartconfigs()

@app.cli.command('debug', help='Start in debug mode.')
def debug():
    app.run(debug=True)

@app.cli.command('debug-with-user', help='Start in debug mode with pre-created user.')
def debug_with_user():
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_chartconfigs()
        from data_visualization.models import User
        User.generate_fake_user('Fake User', 'fakeemail@localhost.loc', 'fakepassword')
    app.run(debug=True)

@app.cli.command('debug-with-datafactory', help='Start in debug mode with datafactory.')
def debug_with_datafactory():
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_chartconfigs()
        from data_visualization.models import User
        User.generate_fake_user('Fake User', 'fakeemail@localhost.loc', 'fakepassword')
    import subprocess
    datafactory_proc = subprocess.Popen(['python', './datafactory.py'])
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        datafactory_proc.kill()

@app.cli.command('debug-with-datareplay', help='Start in debug mode with datareplay.')
def debug_with_datareplay():
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_chartconfigs()
        from data_visualization.models import User
        User.generate_fake_user('Fake User', 'fakeemail@localhost.loc', 'fakepassword')
    import subprocess
    datareplay_proc = subprocess.Popen(['python', './datareplay.py'])
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        datareplay_proc.kill()

@app.cli.command('tests', help='Run unittests.')
@click.option('--name', '-n')
def tests(name):
    import unittest
    if name:
        name = 'tests.' + name
        tests = unittest.TestLoader().loadTestsFromName(name)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
