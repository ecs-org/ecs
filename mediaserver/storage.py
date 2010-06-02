# -*- coding: utf-8 -*-

class Storage(object):
    def store(self, id, bigpage, zoom):
        print 'store (%s, %s, %s)' % (id, bigpage, zoom)

    def load(self, id, bigpage, zoom):
        print 'load (%s, %s, %s)' % (id, bigpage, zoom)
