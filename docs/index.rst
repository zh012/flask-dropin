Flask-DropIn
============

The **Flask-DropIn** makes organizing large flask application easier. You can break your flask app
to multiple `dropins`, which is a similiar concept as Django's app. Flask-DropIn will automatically
pick them up, and assemble different parts into your flask application.

.. contents::
   :local:
   :backlinks: None


Installation
------------

Install with **pip** and **easy_install**::

    pip install flask-dropin

or download the latest version from version control::

    git clone https://github.com/zh012/flask-dropin.git
    cd flask-script
    python setup.py develop

.. _sample-app:

Create a Flask application
--------------------------

Create a folder `testapp`, and a file `app.py` in the folder with following content::

    from flask import Flask
    from flask_dropin import DropInManager

    app = Flask(__name__)
    app.config['DROPINS'] = ['home']
    dropin = DropInManager(app)

    if __name__ == '__main__':
        app.run(debug=True)

Create another file `home.py` in the same folder::

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

Run this app::

    python app.py

Now, open the urls::

    http://localhost:5000/web
    http://localhost:5000/api/version

in browser, you will find that the blueprints are registered to the app automatically.


Dropin
------

Dropin, conceptually like a app in Django project, is usually a python module. It contains
the definition of pieces of the flask app, which is called **drops** and assembled into the
app by DropInManager. The following settings are used to configure the dropins for an appp.

- **DROPINS**

    A list of python modules name. They has to be located in python path in order to be
    importable. In a settings file, it may look like::

        DROPINS = [
            'contrib.auth',
            'articles',
            'extensions.myplugin',
            ...
        ]


- **DROPINS_ITER**

    A callable which take **app** as the only parameter and return a list (or any iterable) of
    dropins name. It could be a set in the way::

        from myapp import discover_dropins
        DROPINS_ITER = discover_dropins

    or using python object path with format `module_name:object_name`::

        DROPINS_ITER = 'myapp:discover_dropins'

    With this setting, you can implement some auto dropin discovering machanism. For example,
    let's define the discover_dropins in `myapp.py` like this::

        import os

        def discover_dropins(app):
            for f in os.list(app.root_path):
                if f.startswith('dropin_') and f.endswith('.py'):
                    yield f[:-3]

    Then, all the modules in the root_path (make sure it is in python path) with name like
    `dropin_foo.py` would be automatically discovered and loaded by DropInManager, with no
    need to put it in DROPINS list manually.


If DROPINS and DROPINS_ITER are both configured. DropInManger will load the DROPINS first,
and then load DROPINS_ITER.


Drops loader
------------

Drops is a list of extensions to enriche the app features. Drops loader imports the drops
from dropins, and register the extensions to flask app.

In order to be imported, the drops should be exposed to the loader following certain
convension. Let's take the `blueprints` as example.

- If the dropin is a python module, you can define a variable `blueprints` as a list of
    blueprints. As shown in :ref:`sample-app`.

- If the dropin is a python package, you can create a `plueprints.py` module in this
    package, and define a variable `__drops__` as a list of blueprints in this module.

- Not only a list type, the `blueprints` could be any iterable.

- Even further the 'blueprints' could be any type of object which has a iterable
    attribute `__drops__`. In this case, the `blueprints.__drops__` will be the real
    blueprints list.

- The `blueprints` or `blueprints.__drops__` can also be a callable. It will be called
    with **app** as the only argument to get the real blueprints list.

Flask-DropIn defined loaders for five types of drops out of box. They are `blueprints`,
`modelewares`, `context_processors`, `models` and `services`. The ways that each loader
imports drops are pretty much the same. However, different drops are assembled into
the app differently.

- **blueprints**

    Default loader: `flask_dropin.BlueprintsLoader`

    No superise, the blueprints are registered to app by calling `app.register_blueprint`.
    But you can customize the `url_prefix` used for each blueprint with settings. ::

        DROPIN_BLUEPRINTS_TRANSFORM = {
            '/web': '',
            '/api/v3': '/api',
            '*': None
        }

    With the settings above, all blueprints with `/web` url prefix will be mounted to root,
    and `/api/v3` to `api`. As the value of `*` is `None`, all blueprints with other url
    prefixes will be ignored.

    If `*` was not shown in this setting, the other blueprintes would be registered as normal.
    The value of `*` can also be a function, take the blueprinte's `url_prefix` as argument,
    and return the prefix used by `app.register_blueprint`.

- **middlewares**

    Default loader: `flask_dropin.MiddlewaresLoader`

    A middleware is an python object which has one or more attributes with name `before_request`,
    `after_request` and  `teardown_request`, and they will be registered to the given app respectively.

- **context_processors**

    Default loader: `flask_dropin.ContextProcessorsLoader`

    A context_processor is a function (or callable) which could be registed by `app.context_processor`.

- **models**

    The models loader stores model objects in ::

        app.extensions['dropin']['models']

    Default loader: `flask_dropin.ModelsLoader`

        The default loader stores model objects into a list.

    Other loader: 'flask_dropin.nameddrops.NamedModelsLoader'

        This loader stores model objects in a flask_dropin.nameddrops.DotDict object, where you can
        use the dotted notation to access the values.

- **services**

    The services loader stores service objects in ::

        `app.extensions['dropin']['services']`

    Default loader: `flask_dropin.ServicesLoader`

        The default loader stores model objects into a list.

    Other loader: 'flask_dropin.nameddrops.NamedServicesLoader'

        This loader stores service objects in a flask_dropin.nameddrops.DotDict object, where you can
        use the dotted notation to access the values.


Customize loaders
-----------------

The setting **DROPS_LOADERS** is used for customize the loaders. The default setting is ::

    DROPS_LOADERS = [
        'flask_dropin:ModelsLoader',
        'flask_dropin:BlueprintsLoader',
        'flask_dropin:MiddlewaresLoader',
        'flask_dropin:ContextProcessorsLoader',
        'flask_dropin:ServicesLoader',
    ]

Your configuration will overwrite the default setting. The following setting will lead to only the
blueprints being loaded. ::

    DROPS_LOADERS = ['flask_dropin:BlueprintsLoader']

You create your own customized loaders to fit your needs and support new drops type.


Dropin manager
--------------

**flask_dropin.DropInManager** is a typical flask extensions. It intialize app in two flavors ::

    dropin = DropInManager(app)

or ::

    dropin = DropInManager()
    dropin.init(app)

Other than that, it provides a shortcut to access the values that the loades stored in each app. In
another word, it is also a proxy to app.extensions['dropin'] dict. For example, if the default
`models` loader, the `dropin.models` will be the list that the loader stored in the app.

Thus, it helps to **decouple** the dropins from each other by avoiding explicitly import from other dropins.

Continue with the app created in in :ref:`sample-app`. Ssaying we have a new dropin `auth.py` ::

    from flask import session

    def login_user(name):
        session['_user_name'] = name

    def logout_user():
        session['_user_name'] = None

    def get_current_user():
        return session.get('_user_name')

    services = [login_user, logout_user, get_current_user]

and update the app config in `app.py` with ::

    app.config['SECRET_KEY'] = 'secret'
    app.config['DROPINS'] = ['home', 'auth']
    app.config['DROPS_LOADERS'] = [
        'flask_dropin:BlueprintsLoader',
        'flask_dropin.nameddrops:NamedServicesLoader']
    app.config['DROPIN_BLUEPRINTS_TRANSFORM'] = {'/web': ''}

then we can send a warmer greeting to the user by update the blueprint `web` in `home.py` ::

    from flask import redirect, url_for
    from app import dropin

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


Api
---

.. module:: flask_dropin
.. autoclass:: DropInManager
.. autoclass:: BaseDropsLoader
   :members: register_drops, load_drops
.. autoclass:: ModelsLoader
.. autoclass:: ServicesLoader
.. autoclass:: BlueprintsLoader
.. autoclass:: MiddlewaresLoader
.. autoclass:: ContextProcessorsLoader

.. module:: flask_dropin.nameddrops
.. autoclass:: NamedModelsLoader
.. autoclass:: NamedServicesLoader


Changes
-------
.. include:: ../CHANGES
