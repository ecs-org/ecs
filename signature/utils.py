# -*- coding: utf-8 -*-
import random
from functools import wraps

from django.core.cache import cache
from django.http import Http404

class SigningDepot(object):
    __DEFAULT_TIMEOUT_SEC=180
   
    def __gen_id(self):
        return '%s' % random.randint(1, int(1e17) - 1)

    def deposit(self, sign_dict):
        pdf_id = self.__gen_id()
        cache.set(pdf_id, sign_dict,  self.__DEFAULT_TIMEOUT_SEC)
        return pdf_id
    
    def get(self, pdf_id):
        return cache.get(pdf_id)

    def pop(self, pdf_id):
        if pdf_id is None:
            return None
        else:
            resdict = cache.get(pdf_id)
            cache.delete(pdf_id);
            return resdict

def with_sign_dict(func):
    @wraps(func)
    def _inner(request, *args, **kwargs):
        request.sign_dict = SigningDepot().get(request.GET.get('pdf-id'))
        if request.sign_dict is None:
            raise Http404('Invalid pdf-id. Probably your signing session expired. Please retry.')
        return func(request, *args, **kwargs)
    return _inner
