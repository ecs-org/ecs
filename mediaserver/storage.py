# -*- coding: utf-8 -*-

import getpass
import memcache
import time

from django.conf import settings


class SetData(object):
    # minimal data to create ImageSet.images data (mostly derived from <pages>)
    # minimal data to to re-render PageData that was squeezed out
    # thus memcache re-fill can avoid SQL lookups if SetData stayed within the cache
    def __init__(self, origin, pdf_name, pages, opt_compress=True, opt_interlace=True):
        self.origin = origin
        self.pdf_name = pdf_name
        self.pages = pages
        self.opt_compress = opt_compress
        self.opt_interlace = opt_interlace

    def __str__(self):
        return '(origin: %s, "%s", page(s): %d, compress: %s, interlace: %s)' % (self.origin, self.pdf_name, self.pages, self.opt_compress, self.opt_interlace)


class PageData(object):
    def __init__(self, png_name):
        self.crit_size = 200 * 1024
        self.png_name = png_name
        self.png_data = None
        self.png_data_size = None
        self.png_time = None

    def __str__(self):
        return '(%s, size %s, %s)' % (self.png_name, self.png_data_size, time.ctime(self.png_time))

    def load_from_file(self):
        f = open(self.png_name, 'rb')
        self.png_data = f.read()
        f.close()
        self.png_data_size = len(self.png_data)
        if self.png_data_size >= self.crit_size:
            delta = (100.0 * (self.png_data_size - self.crit_size)) / self.crit_size
            print "Warning: (len(%s): %d) >= (crit_size: %d) [+%0.2f%%]" % (self.png_name, self.png_data_size, self.crit_size, delta)
        self.png_time = time.time()


class Cache(object):
    def __init__(self):
        self.ns = '%s.ms' % getpass.getuser()
        self.mc = memcache.Client(['%s:%d' % (settings.MEMCACHEDB_HOST, settings.MEMCACHEDB_PORT)], debug=0)

    def get_set_key(self, id):
        return str('%s.%s' % (self.ns, id))

    def store_set(self, id, set_data):
        set_key = self.get_set_key(id)
        return self.mc.set(set_key, set_data)

    def load_set(self, id):
        set_key = self.get_set_key(id)
        return self.mc.get(set_key)

    def get_page_key(self, id, bigpage, zoom):
        return str('%s.%s:%s:%s' % (self.ns, id, bigpage, zoom))

    def store_page(self, id, bigpage, zoom, png_name):
        page_key = self.get_page_key(id, bigpage, zoom)
        page_data = PageData(png_name)
        page_data.load_from_file()
        return self.mc.set(page_key, page_data)

    def load_page(self, id, bigpage, zoom):
        page_key = self.get_page_key(id, bigpage, zoom)
        return self.mc.get(page_key)
