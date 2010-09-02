'''
Created on Aug 26, 2010

@author: elchaschab
'''
from ecs.mediaserver.cacheable import Cacheable

class Docshot(Cacheable):
    '''
    classdocs
    '''

    def __init__(self, tiles_x, tiles_y, width, firstpage, lastpage, uuid=None, lastaccess=None, data=None ):
        '''
        Constructor
        '''
        self.tiles_x=tiles_x
        self.tiles_y=tiles_y
        self.width=width
        self.firstpage=firstpage
        self.lastpage=lastpage

        super(Docshot, self).__init__(self)
    
    def cacheID(self):
        return self.uuid, "_",self.tiles_x, "_", self.tiles_y, "_", self.width, "_", self.firstpage, "_", self.lastpage  

    def validate(self):
        pass