# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#
"""
Urlmap for docstash
"""

from django.conf.urls.defaults import *

from ecs.docstash.decorators import with_docstash_transaction

@with_docstash_transaction
def simple_post_view(request):
    request.docstash.post(request.POST)
    

urlpatterns = patterns('',
    url(r'^simple_post/$', simple_post_view),
)
