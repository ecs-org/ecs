# -*- coding: utf-8 -*-

import memcache
import time


class PageData(object):
    def __init__(self, png_name):
        self.png_name = png_name
        self.png_data = open(png_name, 'r').read()  # TODO check with larger files
        self.png_time = time.time()

    def __str__(self):
        return '(%s, length %d, %s)' % (self.png_name, len(self.png_data), time.ctime(self.png_time))


class Storage(object):
    def __init__(self):
        self.ns = 'media'
        self.mc = memcache.Client(['127.0.0.1:21201'], debug=0)

    def get_key(self, id, bigpage, zoom):
        return '%s:%s:%s:%s' % (self.ns, id, bigpage, zoom)

    def store_page(self, png_name, id, bigpage, zoom):
        key = self.get_key(id, bigpage, zoom)
        print 'store page "%s" as "%s"' % (png_name, key)
        return self.mc.set(key, PageData(png_name))

    def load_page(self, id, bigpage, zoom):
        key = self.get_key(id, bigpage, zoom)
        print 'load page "%s"' % key
        return  self.mc.get(key)
