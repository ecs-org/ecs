# -*- coding: utf-8 -*-

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
