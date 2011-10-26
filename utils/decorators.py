# -*- coding: utf-8 -*-
from datetime import datetime
from functools import wraps

from django.http import Http404
from django.conf import settings

def developer(func):
    """ Wraps a view to raise 404 if settings.DEBUG if False"""
    @wraps(func)
    def _inner(*args, **kwargs):
        if not settings.DEBUG:
            raise Http404()

        return func(*args, **kwargs)

    return _inner


def singleton(cls):
    """ Use a class as singleton. """

    cls.__new_original__ = cls.__new__

    @wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        it =  cls.__dict__.get('__it__')
        if it is not None:
            return it

        cls.__it__ = it = cls.__new_original__(cls, *args, **kw)
        it.__init_original__(*args, **kw)
        return it

    cls.__new__ = singleton_new
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__

    return cls


class print_duration(object):
    def __init__(self, name=None):
        self.name = name
        self.args = ()

    def __enter__(self):
        self.t1 = datetime.now()

    def __exit__(self, *exc):
        self.t2 = datetime.now()
        print '{0} with arguments {1} duration: {2}'.format(self.name or '<anonymous>', self.args, self.t2-self.t1)

    def __call__(self, func):
        if self.name is None:
            self.name = '{0}.{1}'.format(func.__module__, func.__name__)
        @wraps(func)
        def _inner(*args, **kwargs):
            self.args = args
            with self:
                return func(*args, **kwargs)
        return _inner
