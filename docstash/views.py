# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#

"""
docstash API views.
"""

from django.http import HttpResponse
from django.utils.simplejson import dumps

def jsonify(func):
    def wrapper(*args, **kw):
        res = func(*args, **kw)
        return HttpResponse(dumps(res), "text/json")
    return wrapper

@jsonify
def create(request):
    return ["meep"]
