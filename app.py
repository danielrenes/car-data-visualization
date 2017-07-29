#!/usr/bin/env python

import subprocess

from data_visualization import create_app, db
from data_visualization.queries import create_chartconfigs

app = create_app()

@app.cli.command('init-db', help='Create a fresh database')
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_chartconfigs()

@app.cli.command('run-with-datafactory', help='Run server and datafactory')
def run_with_datafactory():
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_chartconfigs()
    datafactory_proc = subprocess.Popen(['python', './datafactory.py'])
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        datafactory_proc.kill()

@app.cli.command('tests', help='Run unittests')
def tests():
    tests = subprocess.call(['python', '-c', 'import tests; tests.run()'])
