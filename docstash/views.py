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
                                  key=key, value="null")
    return [key, obj.token]

def read(request, key):
    obj = list(DocStash.objects.filter(key=key).order_by("-token")[0:1])[0]
    return HttpResponse('["%s", %s]' % (obj.token, obj.value), "text/json")

@jsonify
def search(request):
    res = []
    for obj in DocStash.objects.filter(name__icontains=request.GET["name"], form__icontains=request.GET["form"]):
        res.append(dict(name=obj.name, form=obj.form, modtime="?", key=obj.key))
    return res
          
