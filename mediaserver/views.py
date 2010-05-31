# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from ecs.core.views.utils import render, redirect_to_next_url


def is_int(x):
    try:
        i = int(x)
        return True
    except:
        return False
    

def image(request, id=1, bigpage=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is none!")

    if not is_int(id) or (id < 1):
        return HttpResponse("Error: invalid parameter id = '%s'!" % id)
    id = int(id)

    if not is_int(bigpage):
        return HttpResponse("Error: invalid parameter bigpage = '%s'!" % bigpage)
    bigpage = int(bigpage)

    return HttpResponse("serving image(id = '%s', bigpage = '%s', zoom='%s')" % (id, bigpage, zoom))
