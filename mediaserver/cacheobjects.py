'''
Created on Sep 3, 2010

@author: elchaschab
'''

class MediaBlob(object):
    '''
    A generic cacheable blob
    '''
    def __init__(self, uuid):
        self.uuid = uuid 

    def cacheID(self):
        return self.uuid.get_hex()
        
    def __str__(self):
        return self.cacheID()

    
class Docshot(object):
    '''
    A cacheable preview image of an actual document
    '''
    def __init__(self, mediablob, tiles_x, tiles_y, width, pagenr):
        self.mediablob = mediablob
        self.tiles_x = tiles_x
        self.tiles_y = tiles_y
        self.width = width
        self.pagenr = pagenr
        
    def cacheID(self):
        return "%s_%s_%s_%s_%s" % (self.mediablob.cacheID(), self.tiles_x, self.tiles_y ,self.width, self.pagenr)  

