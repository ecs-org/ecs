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
            
    def cacheID(self):
        return self.uuid.get_hex()
    
    def touch(self):
        self.lastaccess = time.time()
        
    def lastaccess(self):
        return self.lastaccess

    def setData(self, data):
        self.data = data

        if hasattr(self,"validate"):
            self.validate()
        else: 
            raise NotImplemented("Subclasses need to implement validate")

    def getData(self):
        return self.data
