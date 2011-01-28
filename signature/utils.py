# -*- coding: utf-8 -*-

from django.core.cache import cache
import random

class SigningDepot(object):
    __DEFAULT_TIMEOUT_SEC=180
   
    def __gen_id(self):
        return '%s' % random.randint(1, int(1e17) - 1)

    def deposit(self, sign_dict):
        pdf_id = self.__gen_id()

        cache.set(pdf_id, sign_dict,  self.__DEFAULT_TIMEOUT_SEC)
        return pdf_id
    
    def get(self, pdf_id):
        if pdf_id is None:
            return None
        else:
            return cache.get(pdf_id)

    def pop(self, pdf_id):
        if pdf_id is None:
            return None
        else:
            resdict = cache.get(pdf_id)
            cache.delete(pdf_id);
            return resdict
