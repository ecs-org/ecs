'''
Created on Nov 8, 2010

@author: amir
'''

from uuid import uuid4
import tempfile
from ecs.utils.pdfutils import pdf_barcodestamp

class UnsignedVoteDepot(object):
    depot = dict();
   
    def __gen_id(self):
        return uuid4().get_hex();        

    def deposit(self, pdf_file, display_name):
        pdf_id = self.__gen_id();

        t_file = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
        pdf_barcodestamp(pdf_file, t_file, pdf_id)
        t_file.seek(0)

        self.depot[id] = (t_file, display_name);
        return id
    
    def pickup(self, id):
        t_file, display_name = self.depot[id]
        del self.depot[id]
        return t_file, display_name
    
votesDepot = UnsignedVoteDepot();