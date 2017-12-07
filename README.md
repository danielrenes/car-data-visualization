# car-data-visualization

Required packages (on Ubuntu 14.04 and derivatives)
python-pip, python-virtualenv, build-essential, python-dev, libmysqlclient-dev, mysql-server

To install these packages run:
sudo apt-get install python-pip python-virtualenv build-essential python-dev libmysqlclient-dev mysql-server

Project setup
1) Clone or download the repository.
2) In the project root folder run: virtualenv venv
3) You need to create a MySQL database for the project and a user that can access that database.
3) Go into the venv/bin folder and edit the activate script. You need to define the following environment variables there.
     - SECRET_KEY
     - DATABASE_URI
     - CONFIG
     - FLASK_APP
   You can use the following configuration with a few modifications:
     export SECRET_KEY=secret
     export DATABASE_URI=mysql://<username>:<password>@<mysql server ip>/<database name>
     export CONFIG=development
     export FLASK_APP=app.py
  Please note, if you don't set the FLASK_APP environment variable to app.py than you can't use the flask command line interface.
4) Go back to the project root folder and run: source venv/bin/activate

If you issue the flask command you will get a list of commands that you can run.

To run the demo: flask demo
To run the tests: flask tests
