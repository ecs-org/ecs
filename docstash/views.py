# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#

"""
docstash API views.
"""

from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import get_object_or_404
from ecs.docstash.models import DocStash

def jsonify(func):
    def wrapper(*args, **kw):
        res = func(*args, **kw)
        return HttpResponse(simplejson.dumps(res), "text/json")
    return wrapper

@jsonify
def create(request, form=None):
    stash = DocStash.objects.create(form=form)
    return (stash.key, stash.version)

@jsonify
def read(request, key):
    stash = get_object_or_404(DocStash, key=key)
    print stash.version
    return (stash.version, stash.current_value)

@jsonify
def post(request, key, version):
    stash = get_object_or_404(DocStash, key=key)
    stash.start_transaction(int(version))
    stash.value = simplejson.loads(request.raw_post_data)
    stash.commit_transaction()
    return (stash.key, stash.version)
    

          
