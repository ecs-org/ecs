# -*- coding: utf-8 -*-

import hashlib
import os

from django.db import models
from django.test import TestCase


class CacheTest(TestCase):
    id_test = '0'
    origin = 'CacheTest'
    pdf_name = 'foo.pdf'
    pages = 123
    opt_compress = False
    opt_interlace = False
    png_name = os.path.join(os.path.dirname(__file__), 'test-pdf-14-seitig_3x3_big_0002_a7_z.png')
    png_md5 = '207cf4f4e4a04b9b8f6d6b7c1e389260'
    page = 2
    zoom = '3x3'

    def test_set(self):
        return # FIXME/mediaserver
        cache = Cache()
        set_data = SetData(self.origin, self.pdf_name, self.pages, self.opt_compress, self.opt_interlace)
        set_key = cache.get_set_key(self.id_test)
        print 'storing set "%s"' % set_key
        retval = cache.store_set(self.id_test, set_data)
        self.assertNotEqual(retval, 0)        
        set_data = None
        print 'loading set "%s"' % set_key
        set_data = cache.load_set(self.id_test)
        self.assertNotEqual(set_data, None)
        self.assertEqual(set_data.origin, self.origin)
        self.assertEqual(set_data.pdf_name, self.pdf_name)
        self.assertEqual(set_data.pages, self.pages)
        self.assertEqual(set_data.opt_compress, self.opt_compress)
        self.assertEqual(set_data.opt_interlace, self.opt_interlace)

    def test_page(self):
        return # FIXME/mediaserver
        cache = Cache()
        page_data = PageData(self.png_name)
        page_data.load_from_file()
        m = hashlib.md5()
        m.update(page_data.png_data)
        png_data_md5 = m.hexdigest()
        if png_data_md5 != self.png_md5:
            print 'test data file "%s" should have MD5 hash value "%s"!' % (self.png_name, self.png_md5)
            self.assertTrue(False)
        png_data_size = page_data.png_data_size
        png_time = int(page_data.png_time)
        page_key = cache.get_page_key(self.id_test, self.page, self.zoom)
        print 'storing page "%s"' % page_key
        retval = cache.store_page(self.id_test, self.page, self.zoom, self.png_name)
        self.assertNotEqual(retval, 0)
        page_data = None
        print 'loading page "%s"' % page_key
        page_data = cache.load_page(self.id_test, self.page, self.zoom)
        m2 = hashlib.md5()
        m2.update(page_data.png_data)
        md5 = m2.hexdigest()
        self.assertNotEqual(page_data, None)
        self.assertEqual(page_data.png_name, self.png_name)
        self.assertEqual(md5, png_data_md5)
        self.assertEqual(page_data.png_data_size, png_data_size)
        self.assertEqual(int(page_data.png_time), png_time)
