# -*- coding: utf-8 -*-

import os.path

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.servers.basehttp import FileWrapper

from ecs.core.views.utils import render, redirect_to_next_url


def is_int(x):
    try:
        i = int(x)
        return True
    except:
        return False


def image_data(id, bigpage, zoom):
    if id == 1:
        filename = 'ecs-09-submission-form'
    else:
        filename = 'test-pdf-14-seitig'
    if zoom != '1':
        filename += '_' + zoom
    filename += '_%04d.png' % bigpage

    path = os.path.join('static', 'mediaserver', 'images', filename)
    data = open(path, 'r').read()
    return data
    

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

    response = HttpResponse(image_data(id, bigpage, zoom), mimetype='image/png')
    return response
