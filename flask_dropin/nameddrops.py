import six
from . import BaseDropsLoader


class DotDict(object):
    """An object whose attributes could be updated with dict or key/value pair iterable.

    Args:
        initials (dict or key,value iterable, optional): The initial data.
        disable_update (bool, optional): Default: **False**. If true, each
            attribute could only be written one time and trying to assign a
            new value to a existing attribute will lead to a `ValueError`.

    Usage::

        In [1]: from flask_dropin.nameddrops import DotDict

        In [2]: d = DotDict({'val': 1})

        In [3]: print(d.val)
        1

        In [4]: print('val' in d)
        True

        In [5]: d += {'num': 2}

        In [6]: print(d.num)
        2

        In [7]: d.val = 9

        In [8]: print(d)
        {'num': 2, 'val': 9}


        In [9]: d = DotDict({'val': 1}, True)

        In [10]: d.val = 2

        ValueError: key "val" conflict

        In [11]: d += {'val': 2}

        ValueError: key conflict


    """
    __data = None
    __disable_update = None

    def __init__(self, initials=None, disable_update=False):
        self.__data = dict(initials or {})
        self.__disable_update = disable_update

    def __iter__(self):
        return six.iteritems(self.__data)

    def __iadd__(self, other):
        if self.__disable_update and set(self.__data.keys()).intersection(dict(other).keys()):
            raise ValueError('key conflict')
        self.__data.update(other)
        return self

    def __getattr__(self, key):
        try:
            return self.__data[key]
        except KeyError:
            raise AttributeError(key)
    __getitem__ = __getattr__

    def __setattr__(self, key, value):
        if self.__disable_update and key in self.__data:
            raise ValueError('key "%s" conflict' % key)
        if not key.startswith('_%s__' % self.__class__.__name__):
            self.__data[key] = value
        else:
            super(DotDict, self).__setattr__(key, value)
    __setitem__ = __setattr__

    def __str__(self):
        return self.__data.__str__()
    __repr__ = __str__

    def __contains__(self, key):
        return key in self.__data


class BaseNamedDropsLoader(BaseDropsLoader):
    def load_drops(self, dropin):
        drops = super(BaseNamedDropsLoader, self).load_drops(dropin)
        for d in drops:
            if isinstance(d, (list, tuple)):
                yield d
            elif hasattr(d, '__name__'):
                yield d.__name__, d
            elif hasattr(d, 'func_name'):
                yield d.func_name, d
            else:
                yield d

    def register_drops(self, app, dropin):
        drops = app.extensions['dropin'].setdefault(self.drops_type, DotDict(disable_update=True))
        drops += dict(self.load_drops(dropin))


class NamedModelsLoader(BaseNamedDropsLoader):
    """Load drops with type `models`. The difference with to **ModelsLoader** is that this loader
    require the drops to be provided by name/value pairs. These models will be stored in a DotDict
    object, so that it could be referenced by dotted notation. In addition, it will check if there
    is name conflict among the `models` provided by each `dropin`.
    """
    drops_type = 'models'


class NamedServicesLoader(BaseNamedDropsLoader):
    """Load drops with type `services`. Refere to **NamedModelsLoader**.
    """
    drops_type = 'services'
