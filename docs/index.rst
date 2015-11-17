Flask-DropIn
============

The **Flask-DropIn** makes organizing large flask application easier. You can break your to multiple
`dropins`, which is similiar concept as Django's app, and Flask-DropIn will automatically pick them
up, and assemble different parts into your flask application.

.. contents::
   :local:
   :backlinks: None


Installation
------------

Install with **pip** and **easy_install**::

    pip install flask-dropin

or download the latest version from version control::

    git clone https://github.com/smurfix/flask-dropin.git
    cd flask-script
    python setup.py develop


Create a Flask application
--------------------------

As usual, we will have a ```app.py``` file



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
.. autoclass:: DotDict
