# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify


web = Blueprint('web', __name__, url_prefix='/web')


@web.route('/')
def landing():
    return 'Hello!'


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/me')
def me():
    return jsonify(name='jerry', email='jerry@test.com')


blueprints = [web, api]


def get_current_user():
    return 'tester'

services = [
    ('version', '1.1.1'),
    get_current_user
]


def models():
    return 'model 1', 'model 2', 'model 3'
