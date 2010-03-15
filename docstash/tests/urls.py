# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.utils import simplejson
from ecs.docstash.decorators import with_docstash_transaction


@with_docstash_transaction
def simple_post_view(request):
    if request.method == 'POST':
        request.docstash.value = request.POST
    return HttpResponse(simplejson.dumps(request.docstash.value), content_type='text/json')

urlpatterns = patterns('',
    url(r'^simple_post/(?:(?P<docstash_key>.*)/)?$', 'ecs.docstash.tests.urls.simple_post_view'),
)
