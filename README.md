# car-data-visualization

<b>Required packages (on Ubuntu 14.04 and derivatives)</b>

python-pip, python-virtualenv, build-essential, python-dev, libmysqlclient-dev, mysql-server

<b>To install these packages run:</b>

sudo apt-get install python-pip python-virtualenv build-essential python-dev libmysqlclient-dev mysql-server

<b> Project setup </b>
1) Clone or download the repository.
2) In the project root folder run: <strong>virtualenv venv</strong>
3) You need to create a MySQL database for the project and a user that can access that database.
4) Go into the venv/bin folder and edit the activate script. You need to define the following environment variables there.
     - SECRET_KEY
     - DATABASE_URI
     - CONFIG
     - FLASK_APP
     
   You can use the following configuration with a few modifications:
   
       export SECRET_KEY=secret
     
       export DATABASE_URI=mysql://<username>:<password>@<mysql server ip>/<database name>
     
       export CONFIG=development
     
       export FLASK_APP=app.py
  
   Please note, if you don't set the <strong>FLASK_APP</strong> environment variable to <strong>app.py</strong> than you can't use the flask command line interface.
  
5) Go back to the project root folder and run: <strong>source venv/bin/activate</strong>
6) Install the required python packages: <strong>pip install -r requirements.txt</strong>

If you issue the <strong>flask</strong> command you will get a list of commands that you can run.

To run the demo: <strong>flask demo</strong>

To run the tests: <strong>flask tests</strong>
