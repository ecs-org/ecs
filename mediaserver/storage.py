# -*- coding: utf-8 -*-

import memcache
import time


class SetData(object):
    def __init__(self, pages):
        self.pages = pages

    def __str__(self):
        return '(%d page(s))' % self.pages


class PageData(object):
    def __init__(self, png_name):
        crit_size = 200 * 1024
        self.png_name = png_name
        f = open(self.png_name, 'rb')
        self.png_data = f.read()
        f.close()
        self.png_data_size = len(self.png_data)
        if self.png_data_size >= crit_size:
            delta = (100.0 * (self.png_data_size - crit_size)) / crit_size
            print "Warning: (len(%s): %d) >= (crit_size: %d) [+%0.2f%%]" % (self.png_name, self.png_data_size, crit_size, delta)
        self.png_time = time.time()

    def __str__(self):
        return '(%s, size %d, %s)' % (self.png_name, self.png_data_size, time.ctime(self.png_time))


class Storage(object):
    def __init__(self):
        self.ns = 'media'
        port_memcached = 11211
        port_memcachedb = 21201
        host = '127.0.0.1'
        self.mc = memcache.Client(['%s:%d' % (host, port_memcachedb)], debug=0)

    def get_set_key(self, id):
        return str('%s:%s' % (self.ns, id))

    def store_set(self, pages, id):
        set_key = self.get_set_key(id)
        print 'storing set "%s" as "%s"' % (id, set_key)
        set_data = SetData(pages)
        return self.mc.set(set_key, set_data)

    def load_set(self, id):
        set_key = self.get_set_key(id)
        print 'loading set "%s"' % set_key
        return self.mc.get(set_key)

    def get_page_key(self, id, bigpage, zoom):
        return str('%s:%s:%s:%s' % (self.ns, id, bigpage, zoom))

    def store_page(self, png_name, id, bigpage, zoom):
        page_key = self.get_page_key(id, bigpage, zoom)
        print 'storing page "%s" as "%s"' % (png_name, page_key)
        page_data = PageData(png_name)
        return self.mc.set(page_key, page_data)

    def load_page(self, id, bigpage, zoom):
        page_key = self.get_page_key(id, bigpage, zoom)
        print 'loading page "%s"' % page_key
        return self.mc.get(page_key)
