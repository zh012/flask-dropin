from flask import Blueprint, jsonify, redirect, url_for
from app import dropin

web = Blueprint('home_web', __name__, url_prefix='/web')


@web.route('/')
def landing():
    return 'Hello {}!'.format(dropin.services.get_current_user())


@web.route('/login/<username>')
def login_me(username):
    dropin.services.login_user(username)
    return redirect(url_for('.landing'))


@web.route('/logout')
def logout_me():
    dropin.services.logout_user()
    return redirect(url_for('.landing'))


api = Blueprint('home_api', __name__, url_prefix='/api')


@api.route('/version')
def myprofile():
    return jsonify(version='0.0.0')

blueprints = [web, api]
