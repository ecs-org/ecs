import anyjson
from functools import wraps

from django.conf import settings
from django.utils import translation


def translate(func):
    @wraps(func)
    def _inner(*args, **kwargs):
        lang = kwargs.pop('language', settings.LANGUAGE_CODE)
        prev_lang = translation.get_language()
        translation.activate(lang)
        try:
            ret = func(*args, **kwargs)
        finally:
            translation.activate(prev_lang)
        return ret
    return _inner
