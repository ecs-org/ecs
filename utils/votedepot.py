'''
Created on Nov 8, 2010

@author: amir
'''
from django.core.cache import cache
import random

class VoteDepot(object):
    __DEFAULT_TIMEOUT_SEC=180
    depot = dict()
   
    def __gen_id(self):
        return '%s' % random.randint(1, int(1e17) - 1)

    def deposit(self, pdf_data, html_data, document_uuid, display_name):
        pdf_id = self.__gen_id()

        cache.set(pdf_id, {"pdf_data": pdf_data, "html_data": html_data, "uuid": document_uuid, "name": display_name}, self.__DEFAULT_TIMEOUT_SEC)
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
