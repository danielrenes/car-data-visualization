from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html.j2')

@main.route('/<username>', methods=['GET'])
def userpage(username):
    return render_template('userpage.html.j2', username=username)
