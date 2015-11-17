from flask import Blueprint, render_template, jsonify
from flask_dropin import DropInManager

dropin = DropInManager()

web = Blueprint('home_web', __name__, url_prefix='/web', template_folder='templates')


@web.route('/')
def landing():
    get_current_user = dict(dropin.services)['get_current_user']
    user = get_current_user()
    return user and 'Hello {}!'.format(user) or 'Please login!'


api = Blueprint('home_api', __name__, url_prefix='/api')


@api.route('/me')
def myprofile():
    get_current_user = dict(dropin.services)['get_current_user']
    return jsonify(username=get_current_user())


blueprints = [web, api]
