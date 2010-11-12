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

        print "deposit: %s, len: %d, name: %s, uuid: %s" % (pdf_id, len(pdf_data), display_name, document_uuid)
        cache.set(pdf_id, {"pdf_data": pdf_data, "html_data": html_data, "uuid": document_uuid, "name": display_name}, self.__DEFAULT_TIMEOUT_SEC)
        return pdf_id
    
    def get(self, pdf_id):
        print "get: ", pdf_id
        return cache.get(pdf_id)

    def pop(self, pdf_id):
        print "pop: ", pdf_id
        resdict = cache.get(pdf_id)
        cache.delete(pdf_id);
        return resdict
