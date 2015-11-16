# -*- coding: utf-8 -*-
import six
from flask import current_app


def load_object(obj_name):
    if ':' in obj_name:
        mod, name = obj_name.split(':')
    else:
        mod, name = obj_name, None
    mod = __import__(mod, fromlist=[''])
    if name:
        return getattr(mod, name)
    return mod


class BaseDropsLoader(object):
    """Load `drops` from python source code and register those to flask app.
    Base class of other loaders.

    Attributes:
        drops_type (string): The name of drops type. It is used to locate
            the drops.

    """
    drops_type = None

    def load_drops(self, dropin):
        """Load `drops` from the given dropin.

        Args:
            dropin (string): path of a dropin, e.g. dropin.auth

        Returns:
            An iterable contains the drops object in the given dropin

        This method load drops object by some sort of convension. For example, assuming
        we want to load drops type `models` from dropin `dropin.articls`. The drops are
        discoveried with the following sequence::

            import dropin.articles
            drops = dropin.articles.models

        if anything goes wrong, next try is ::

            import dropin.articles.models as drops

        if the current drops object has attribute **__drops__**::

            drops = drops.__drops__

        if the current drops object is a callable::

            drops = drops()

        now, the drops will be returned.

        if not drops was found, an empty list is returned.

        """
        obj = load_object(dropin)
        try:
            drops = getattr(obj, self.drops_type)
        except AttributeError:
            try:
                drops = load_object('%s.%s' % (dropin, self.drops_type))
            except ImportError:
                drops = None
        if hasattr(drops, '__drops__'):
            drops = drops.__drops__
        if callable(drops):
            drops = drops()
        return drops or []

    def register_drops(self, app, dropin):
        """Register the `drops` in given `dropin` to a flask app.

        Args:
            app (Flask): the flask app to be initialized
            dropin (string): path of a python module or object, e.g. dropin.auth


        This is the only method that a drops loader **must** implment. The default
        behavior in the base loader is to store all the drops object in the app's
        extentions dict.

        For example, the drops with type `models` will be stored in a list which
        is accessible through::

            app.extensions['dropin']['models']

        or through DropInManager instance which provide a simple proxy to the dropin
        extension of `current_app`::

            dropin = DropInManager()
            dropin.models

        Whereas the BlueprintsLoader overrided this method to actually register
        the blueprints to the app.
        """
        drops = app.extensions['dropin'].setdefault(self.drops_type, [])
        drops.extend(self.load_drops(dropin))


class ModelsLoader(BaseDropsLoader):
    """Load `drops` with type `models`.
    """
    drops_type = 'models'


class ServicesLoader(BaseDropsLoader):
    """Load `drops` with type `services`.
    """
    drops_type = 'services'


class BlueprintsLoader(BaseDropsLoader):
    """Load `drops` with type `blueprints`, and register blueprints to flask app.
    """
    drops_type = 'blueprints'

    def register_drops(self, app, dropin):
        trans = app.config.get('DROPIN_BLUEPRINTS_TRANSFORM') or {}
        if '*' in trans:
            default_trans = trans['*']
        else:
            default_trans = lambda pf: None
        for bp in self.load_drops(dropin):
            if bp.url_prefix in trans:
                app.register_blueprint(bp, url_prefix=trans[bp.url_prefix])
            elif default_trans:
                app.register_blueprint(bp, url_prefix=default_trans(bp.url_prefix))


class MiddlewaresLoader(BaseDropsLoader):
    """Load `drops` with type `middlewares`, and register middlewares to flask app.

    The `before_request`, `after_request` and `teardown_request` attributes will be
    registered to the given app respectively.
    """
    drops_type = 'middlewares'

    def register_drops(self, app, dropin):
        for mw in self.load_drops(dropin):
            for cb in ['before_request', 'after_request', 'teardown_request']:
                if hasattr(mw, cb):
                    getattr(app, cb)(getattr(mw, cb))


class ContextProcessorsLoader(BaseDropsLoader):
    """Load `drops` with type `context_processors`, and register context_processors to flask app.
    """
    drops_type = 'context_processors'

    def register_drops(self, app, dropin):
        for cp in self.load_drops(dropin):
            app.context_processor(cp)


default_loaders = [
    ModelsLoader,
    BlueprintsLoader,
    MiddlewaresLoader,
    ContextProcessorsLoader,
    ServicesLoader,
]


class DropInManager(object):
    """A flask extension to initialize flask app with activated dropins, and also provide
    shortcut to access drops object if avialable.

    Its behavior is controled by three settings.

    **DROPINS**: a list of python object path for ativated dropins.

    **DROPINS_ITER**: a callable (or python path to the callable) which return a list of dropins.

    **DROPIN_LOADERS**: a list of drops loader (or python path to drops loader). If not provided,
    ther following loaders will be used::

            [
                flask_dropin.ModelsLoader,
                flask_dropin.BlueprintsLoader,
                flask_dropin.MiddlewaresLoader,
                flask_dropin.ContextProcessorsLoader,
                flask_dropin.ServicesLoader,
            ]

    """
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def iter_loaders(self, app):
        for l in app.config.get('DROPS_LOADERS', default_loaders):
            if isinstance(l, six.string_types):
                l = load_object(l)
            if callable(l):
                l = l()
            yield l

    def iter_dropins(self, app):
        for dropin in app.config.get('DROPINS') or []:
            yield dropin
        dropins_iter = app.config.get('DROPINS_ITER')
        if dropins_iter:
            if isinstance(dropins_iter, six.string_types):
                dropins_iter = load_object(dropins_iter)
            if callable(dropins_iter):
                dropins_iter = dropins_iter(app)
            for dropin in dropins_iter:
                yield dropin

    def init_app(self, app, slots=None):
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        # only do the initiation if the app was never inited
        if app.extensions.get('dropin') is None:
            app.extensions['dropin'] = {}
            for drops_loader in self.iter_loaders(app):
                for dropin in self.iter_dropins(app):
                    drops_loader.register_drops(app, dropin)

    def __getattr__(self, key):
        try:
            return current_app.extensions['dropin'][key]
        except KeyError:
            raise AttributeError(key)
