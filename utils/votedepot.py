'''
Created on Nov 8, 2010

@author: amir
'''

import tempfile
from ecs.utils.pdfutils import pdf_barcodestamp
from django.core.cache import cache
import random
import os

class VoteDepot(object):
    __DEFAULT_TIMEOUT_SEC=60
    depot = dict()
   
    def __gen_id(self):
        return '%s' % random.randint(1, int(1e17) - 1)

    def deposit(self, pdf_data, document_uuid, display_name):
        pdf_id = self.__gen_id()

        t_in = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
        t_out = tempfile.NamedTemporaryFile(prefix='vote_sign_stamped_', suffix='.pdf', delete=False)
        t_in.write(pdf_data)
        t_in.seek(0)
        pdf_barcodestamp(t_in, t_out, pdf_id)
        t_in.close();
        t_out.seek(0)
	

        cache.set(pdf_id, {"data": t_out.read(), "uuid": document_uuid, "name": display_name}, self.__DEFAULT_TIMEOUT_SEC)
        return pdf_id
    
    def get(self, pdf_id):
        return cache.get(pdf_id)

    def pop(self, pdf_id):
        resdict = cache.get(pdf_id)
        cache.delete(pdf_id);
        return resdict
