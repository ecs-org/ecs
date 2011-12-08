# -*- coding: utf-8 -*-
import random
from functools import wraps

from django.core.cache import cache
from django.http import Http404

class SigningDepot(object):
    __DEFAULT_TIMEOUT_SEC=180
   
    def _gen_id(self):
        return '%s' % random.randint(1, int(1e17) - 1)

    def _get_key(self, prefix, oid):
        return 'sign-{0}-{1}'.format(prefix, oid)

    def deposit(self, prefix, data):
        oid = self._gen_id()
        cache.set(self._get_key(prefix, oid), data,  self.__DEFAULT_TIMEOUT_SEC)
        return oid 
    
    def get(self, prefix, oid):
        return cache.get(self._get_key(prefix, oid))

    def delete(self, prefix, oid):
        cache.delete(self._get_key(prefix, oid));

def with_sign_data(func):
    @wraps(func)
    def _inner(request, *args, **kwargs):
        depot = SigningDepot()
        request.pdf_id = request.GET.get('pdf-id', kwargs.pop('pdf_id', None))
        request.sign_data = depot.get('data', request.pdf_id)
        if request.pdf_id is None or request.sign_data is None:
            raise Http404('Invalid pdf-id. Probably your signing session expired. Please retry.')
        request.sign_session_id = request.sign_data.get('sign_session_id')
        request.sign_session = depot.get('session', request.sign_session_id)
        return func(request, *args, **kwargs)
    return _inner
