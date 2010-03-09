# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#

"""
docstash API views.
"""

from django.http import HttpResponse
from django.utils.simplejson import dumps
from ecs.docstash.models import DocStash
import hashlib

def jsonify(func):
    def wrapper(*args, **kw):
        res = func(*args, **kw)
        return HttpResponse(dumps(res), "text/json")
    return wrapper

@jsonify
def create(request):
    key = hashlib.new("sha", u"%s|%s" % (request.POST["name"], request.POST["form"])).hexdigest()
    obj = DocStash.objects.create(name=request.POST["name"], form=request.POST["form"], 
                                  key=key, value=dumps(None))
    return [key, obj.token]

@jsonify
def read(request, key):
    pass
