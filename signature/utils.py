# -*- coding: utf-8 -*-
import random
from functools import wraps

from django.core.cache import cache
from django.http import Http404

class SigningData(dict):
    def __init__(self, *args, **kwargs):
        super(SigningData, self).__init__(*args, **kwargs)
        self.id = None

    def _gen_id(self):
        return '%s' % random.randint(1, int(1e17) - 1)

    @classmethod
    def retrieve(cls, id):
        data = cache.get(id)
        if not data is None:
            data = cls(data)
            data.id = id
        return data

    def store(self, timeout=None):
        if not self.id:
            self.id = self._gen_id()
        cache.set(self.id, dict(self), timeout)

    def delete(self):
        if self.id:
            cache.delete(self.id)

def with_sign_data(func):
    @wraps(func)
    def _inner(request, *args, **kwargs):
        pdf_id = request.GET.get('pdf-id', kwargs.pop('pdf_id', None))
        request.sign_data = SigningData.retrieve(pdf_id)
        if request.sign_data is None:
            raise Http404('Invalid pdf-id. Probably your signing session expired. Please retry.')
        request.sign_session = SigningData.retrieve(request.sign_data.get('sign_session_id'))
        return func(request, *args, **kwargs)
    return _inner
