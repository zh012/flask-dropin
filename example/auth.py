from flask import session


def login_user(name):
    session['_user_name'] = name


def logout_user():
    session['_user_name'] = None


def get_current_user():
    return session.get('_user_name')

services = [login_user, logout_user, get_current_user]
