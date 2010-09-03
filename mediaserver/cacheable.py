'''
Created on Aug 28, 2010

@author: amir
'''

import time
from uuid import uuid4

class Cacheable(object):
    '''
    classdocs
    '''
    data=None
    def __init__(self, uuid=None, lastaccess=None, data=None):
        '''
        Constructor
        '''

        if not uuid:
            self.uuid = uuid4()
        else:
            self.uuid=uuid

        if not lastaccess:
            self.lastaccess = time.time()
        else: 
            self.lastaccess = lastaccess 

        if data:
            self.setData(data)
            
            
           
        print "cacheable constr", self.uuid
            
    def cacheID(self):
        if hasattr(self.uuid,"get_hex"): 
            return self.uuid.get_hex()
        else:
            return self.uuid
    
    def touch(self):
        self.lastaccess = time.time()
        
    def lastaccess(self):
        return self.lastaccess

        return self.data
