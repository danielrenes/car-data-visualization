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

@app.cli.command('demo', help='Start in debug mode with datareplay.')
def debug_with_datareplay():
    import subprocess
    subprocess.call(['python', './generate_parkingspace_datadefinitions.py', '-c', '20', '-t', '60', '-n', '4', '-x', '8', '-a', '47.475382', '-o', '19.056040', '-r', '0.0025'])
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_chartconfigs()
        from data_visualization.models import User
        User.generate_fake_user('Fake User', 'fakeemail@localhost.loc', 'fakepassword')
    datareplay_proc = subprocess.Popen(['python', './datareplay.py'])
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        datareplay_proc.kill()

@app.cli.command('cleanup', help='Delete all generated files.')
def cleanup():
    data_definitions_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data_definitions')
    generated_files = {
        data_definitions_dir: ['parking_space']
    }
    delete_files = []
    for basedir, filenames in generated_files.iteritems():
        for _file in os.listdir(basedir):
            if os.path.isfile(os.path.join(basedir, _file)):
                for filename in filenames:
                    if _file.startswith(filename):
                        delete_files.append(os.path.join(basedir, _file))
    print 'Files removed:'
    for delete_file in delete_files:
        os.remove(delete_file)
        print delete_file

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
