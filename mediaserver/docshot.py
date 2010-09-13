'''
Created on Aug 26, 2010

@author: elchaschab
'''
from ecs.mediaserver.cacheable import Cacheable

class Docshot(Cacheable):
    '''
    classdocs
    '''

    def __init__(self, tiles_x, tiles_y, width, pagenr,**kwargs ):
        '''
        Constructor
        '''
        self.tiles_x=tiles_x
        self.tiles_y=tiles_y
        self.width=width
        self.pagenr=pagenr

        super(Docshot, self).__init__(**kwargs)
        print "docshot constr:", self.uuid
    
    def cacheID(self):
        return "docshot_%s_%s_%s_%s_%s" % (super(Docshot, self).cacheID(), self.tiles_x, self.tiles_y ,self.width,self.pagenr)  

    def validate(self):
        pass