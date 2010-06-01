# -*- coding: utf-8 -*-

import os.path

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.servers.basehttp import FileWrapper

from ecs.core.views.utils import render, redirect_to_next_url


def get_image_data(id, bigpage, zoom):
    if id == 1:
        filename = 'ecs-09-submission-form'
    else:
        filename = 'test-pdf-14-seitig'
    filename += '_%s_%04d.png' % (zoom, bigpage)

    path = os.path.join('static', 'mediaserver', 'images', filename)
    image_data = open(path, 'r').read()
    return image_data
    

def get_image(request, id=1, bigpage=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is None!")
    id = int(id)
    bigpage = int(bigpage)

    response = HttpResponse(get_image_data(id, bigpage, zoom), mimetype='image/png')
    return response
