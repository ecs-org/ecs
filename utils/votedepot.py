'''
Created on Nov 8, 2010

@author: amir
'''

from uuid import uuid4
import tempfile
from ecs.utils.pdfutils import pdf_barcodestamp
from django.core.cache import cache

class VoteDepot(object):
    __DEFAULT_TIMEOUT_SEC=60
    depot = dict()
   
    def __gen_id(self):
        return uuid4().get_hex()        

    def deposit(self, pdf_data, display_name):
        pdf_id = self.__gen_id()

        t_in = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
        t_out = tempfile.NamedTemporaryFile(prefix='vote_sign_stamped_', suffix='.pdf', delete=False)
        t_in.write(pdf_data)
        t_in.seek(0)
        pdf_barcodestamp(t_in, t_out, pdf_id)
        t_in.close();
        t_out.seek(0)

        cache.set(pdf_id, (t_out.name, display_name), self.__DEFAULT_TIMEOUT_SEC)
        return pdf_id
    
    def pickup(self, id):
        t_file_name, display_name = cache.get(id)
        cache.delete(id)
        return open(t_file_name,'rwb'), display_name
