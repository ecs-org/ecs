# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#

"""
docstash API views.
"""

from django.http import HttpResponse

def create(request):
    return HttpResponse("meep" + request.POST["name"])
