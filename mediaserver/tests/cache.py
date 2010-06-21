# -*- coding: utf-8 -*-

from django.db import models
from django.test import TestCase

from ecs.mediaserver.storage import Cache


class CacheTest(TestCase):
    id = '0'
    origin = 'CacheTest'
    pdf_name = 'foo.pdf'
    pages = 123
    opt_compress = False
    opt_interlace = False

    def test_set(self):
        cache = Cache()
        set_data = SetData(self.origin, self.pdf_name, self.pages, self.opt_compress, self.opt_interlace)
        set_key = cache.get_set_key(self.id)
        print 'storing set "%s"' % set_key
        retval = cache.store_set(self.id, set_data)
        self.assertNotEqual(retval, 0)        
        set_data = None
        print 'loading set "%s"' % set_key
        set_data = cache.load_set(self.id)
        self.assertNotEqual(set_data, None)
        self.assertEqual(set_data.origin, self.origin)
        self.assertEqual(set_data.pdf_name, self.pdf_name)
        self.assertEqual(set_data.pages, self.pages)
        self.assertEqual(set_data.opt_compress, self.opt_compress)
        self.assertEqual(set_data.opt_interlace, self.opt_interlace)
