[![](https://img.shields.io/shippable/564b73031895ca447423b473.svg)](https://app.shippable.com/builds/564b892b34a1910d00295bfb)

Flask-DropIn
============

The **Flask-DropIn** makes organizing large flask application easier. You can break your to multiple
`dropins`, which is similiar concept as Django's app, and Flask-DropIn will automatically pick them
up, and assemble different parts into your flask application.

Read the full [documentation](https://pythonhosted.org/Flask-DropIn/).

Installation
------------

Install with **pip** and **easy_install**

    pip install flask-dropin

or download the latest version from version control

    git clone https://github.com/zh012/flask-dropin.git
    cd flask-dropin
    python setup.py develop


Create a Flask application
--------------------------

Create a folder `testapp`, and a file `app.py` in the folder with following content

    from flask import Flask
    from flask_dropin import DropInManager

    app = Flask(__name__)
    app.config['DROPINS'] = ['home']
    dropin = DropInManager(app)

    if __name__ == '__main__':
        app.run(debug=True)

Create another file `home.py` in the same folder

    from flask import Blueprint, jsonify

    web = Blueprint('home_web', __name__, url_prefix='/web')

    @web.route('/')
    def landing():
        return 'Hello world!'

    api = Blueprint('home_api', __name__, url_prefix='/api')

    @api.route('/version')
    def myprofile():
        return jsonify(version='0.0.0')

    blueprints = [web, api]

Run this app

    python app.py

Now, open the urls

    http://localhost:5000/web
    http://localhost:5000/api/version

in browser, you will find that the blueprints are registered to the app automatically.

