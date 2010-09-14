# -*- coding: utf-8 -*-

import os

from django.core import management
from django.db import models
from django.test import TestCase


class RendererTest(TestCase):
    pdf_name = 'test-pdf-14-seitig.pdf'
    id_test = '0'
    pages = 14

    def setUp(self):
        cache = Cache()
        set_key = cache.get_set_key(self.id_test)
        print 'removing set "%s" from cache .. ' % set_key, cache.mc.delete(set_key)
        image_set = ImageSet(self.id_test)
        page_set = range(1, self.pages + 1)
        for zoom in image_set.render_set.zoom_list:
            for page in page_set:
                page_key = cache.get_page_key(self.id_test, page, zoom)
                print 'removing page "%s" from cache .. ' % page_key, cache.mc.delete(page_key)
        print 'cache cleaned'

    def test_cmd(self):
        pdf_fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.pdf_name)
        print("rendering %s as id %s" % (pdf_fname, str(self.id_test)))
        management.call_command('render', pdf_fname, self.id_test)
