from flask import Blueprint, session, redirect


web = Blueprint('login_web', __name__, url_prefix='/web')


@web.route('/login/<username>')
def login(username):
    session['_current_user'] = username
    return ''


@web.route('/logout')
def logout(username):
    session['_current_user'] = None
    return ''

blueprints = [web]


def get_current_user():
    return session.get('_current_user')

services = [
    get_current_user
]
