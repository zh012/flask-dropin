import json
import pytest


def test_dotdict():
    from flask_dropin.nameddrops import DotDict

    d = DotDict({'val': 100}, True)
    assert d.val == 100
    assert hasattr(d, 'val')
    assert 'val' in d
    with pytest.raises(ValueError):
        d.val = 200
    with pytest.raises(AttributeError):
        d.bad_key

    d += {'num': 999}
    assert d.num == 999
    with pytest.raises(ValueError):
        d += {'num': 888}

    d2 = DotDict({'val': 0}, False)
    d2.val = 1
    assert d2.val == 1
    d2 += {'val': 2}
    assert d2.val == 2
    d2 += d
    assert d2.num == 999


def test_load_object():
    from flask_dropin import load_object
    path = load_object('os.path')
    isdir = load_object('os.path:isdir')
    import os.path
    assert path is os.path
    assert isdir is os.path.isdir


dropin_configs = [
    {
        'DROPINS': ['dropins.allinone'],
        'DROPS_LOADERS': [
            'flask_dropin:ModelsLoader',
            'flask_dropin:BlueprintsLoader',
            'flask_dropin.nameddrops:NamedServicesLoader',
            'flask_dropin:MiddlewaresLoader',
        ]
    },
    {
        'DROPINS': ['dropins.seperate'],
        'DROPS_LOADERS': [
            'flask_dropin:ModelsLoader',
            'flask_dropin:BlueprintsLoader',
            'flask_dropin.nameddrops:NamedServicesLoader',
            'flask_dropin:MiddlewaresLoader',
        ]
    },
    {
        'DROPINS_ITER': lambda a: ['dropins.seperate'],
        'DROPS_LOADERS': [
            'flask_dropin:ModelsLoader',
            'flask_dropin:BlueprintsLoader',
            'flask_dropin.nameddrops:NamedServicesLoader',
            'flask_dropin:MiddlewaresLoader',
        ]
    },
    {
        'DROPINS_ITER': 'dropins.custom:dropin_iter',
        'DROPS_LOADERS': [
            'flask_dropin:ModelsLoader',
            'flask_dropin:BlueprintsLoader',
            'flask_dropin.nameddrops:NamedServicesLoader',
            'flask_dropin:MiddlewaresLoader',
        ]
    }
]


def setup_app(config):
    from flask import Flask
    from flask_dropin import DropInManager
    app = Flask('test')
    app.config.update(config)
    dropin = DropInManager(app)
    return app, dropin


@pytest.mark.parametrize('config', dropin_configs)
def test_dropin(config):
    app, dropin = setup_app(config)
    with app.app_context():
        assert dropin.models[1] == 'model 2'
        assert dropin.services.version == '1.1.1'
        assert dropin.services.get_current_user() == 'tester'
    with app.test_client() as c:
        assert c.get('/web', follow_redirects=True).data == 'Hello!'
        assert json.loads(c.get('/api/me', follow_redirects=True).data)['name'] == 'jerry'


def test_blueprint_transform():
    app, dropin = setup_app({
        'DROPINS': ['dropins.allinone'],
        'DROPS_LOADERS': ['flask_dropin:BlueprintsLoader'],
        'DROPIN_BLUEPRINTS_TRANSFORM': {
            '/web': '/',
            '*': lambda pf: '/tr' + pf
        }
    })

    with app.test_client() as c:
        assert c.get('/web', follow_redirects=True).status_code == 404
        assert c.get('/', follow_redirects=True).data == 'Hello!'
        assert json.loads(c.get('/tr/api/me', follow_redirects=True).data)['name'] == 'jerry'


def test_blueprint_transform_mask():
    app, dropin = setup_app({
        'DROPINS': ['dropins.allinone'],
        'DROPS_LOADERS': ['flask_dropin:BlueprintsLoader'],
        'DROPIN_BLUEPRINTS_TRANSFORM': {
            '/web': '/',
            '*': None
        }
    })

    with app.test_client() as c:
        assert c.get('/', follow_redirects=True).data == 'Hello!'
        assert c.get('/web', follow_redirects=True).status_code == 404
        assert c.get('/api/me', follow_redirects=True).status_code == 404
