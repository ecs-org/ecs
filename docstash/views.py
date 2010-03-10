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
import uuid

def jsonify(func):
    def wrapper(*args, **kw):
        res = func(*args, **kw)
        return HttpResponse(dumps(res), "text/json")
    return wrapper

@jsonify
def create(request):
    key = uuid.uuid4().hex
    obj = DocStash.objects.create(name=request.POST["name"], form=request.POST["form"], 
                                  key=key, value="null")
    return [key, obj.token]

def read(request, key):
    obj = list(DocStash.objects.filter(key=key).order_by("-token")[0:1])[0]
    return HttpResponse('["%s", %s]' % (obj.token, obj.value), "text/json")

@jsonify
def search(request):
    res = {}
    for obj in DocStash.objects.filter(name__icontains=request.GET["name"], form__icontains=request.GET["form"]):
        res.setdefault(obj.key, obj)
        if res[obj.key].token < obj.token:
            res[obj.key] = obj
    result = []
    for obj in res.values():
        result.append(dict(name=obj.name, form=obj.form, modtime=int(obj.modtime.strftime("%s")), key=obj.key))
    return result

@jsonify
def post(request, key, token):
    if len(DocStash.objects.filter(key=key, token__gt=token)) > 0:
        raise ValueError()      # make this thread safe :(
    old = DocStash.objects.get(token=token)
    DocStash.objects.create(key=key, name=old.name, form=old.form, value=request.raw_post_data)
    

          
