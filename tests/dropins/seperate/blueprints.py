from flask import Blueprint, jsonify


web = Blueprint('web', __name__, url_prefix='/web')


@web.route('/')
def landing():
    return 'Hello!'


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/me')
def me():
    return jsonify(name='jerry', email='jerry@test.com')


__drops__ = [web, api]
