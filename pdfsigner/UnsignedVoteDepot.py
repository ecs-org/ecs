'''
Created on Nov 8, 2010

@author: amir
'''

from uuid import uuid4
import tempfile
from ecs.utils.pdfutils import pdf_barcodestamp
from django.core.cache import cache

class UnsignedVoteDepot(object):
    __DEFAULT_TIMEOUT_SEC=60
    depot = dict()
   
    def __gen_id(self):
        return uuid4().get_hex()        

    def deposit(self, pdf_file, display_name):
        pdf_id = self.__gen_id()

        t_file = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
        pdf_barcodestamp(pdf_file, t_file, pdf_id)
        t_file.seek(0)
        cache.set(id, (t_file, display_name), self.__DEFAULT_TIMEOUT_SEC)
        return id
    
    def pickup(self, id):
        t_file, display_name = cache.get(id)
        cache.delete(id)
        return t_file, display_name
