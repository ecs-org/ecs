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
        self.kwargs = {}

    def __enter__(self):
        self.t1 = datetime.now()

    def __exit__(self, *exc):
        self.t2 = datetime.now()
        d = self.t2 - self.t1
        s = '{0:.2f}s {1}'.format(d.total_seconds(), self.name or '<anonymous>')
        if self.args or self.kwargs:
            bits = []
            for arg in self.args:
                bits += [repr(arg)]
            for k, v in self.kwargs.iteritems():
                bits += ['{0}={1}'.format(k, repr(v))]
            s += '(' + ', '.join(bits) + ') '
        print s

    def __call__(self, func):
        if self.name is None:
            self.name = '{0}.{1}'.format(func.__module__, func.__name__)
        @wraps(func)
        def _inner(*args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            with self:
                return func(*args, **kwargs)
        return _inner
