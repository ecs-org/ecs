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


