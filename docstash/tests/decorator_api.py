# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#

"""
Unittests for docstash API
"""

from django.test import TestCase
from ecs.docstash.models import DocStash

class DecoratorApiTest(TestCase):
    def test_simple_post(self):
        self.client.post('simple_post/', {'foo': 'bar'})
        D
        
