# -*- coding: utf-8 -*-

import email.utils
import os.path
import time

from django.http import HttpResponse
from django.conf import settings


def get_image_data(id, bigpage, zoom):
    if id == 1:
        filename = 'ecs-09-submission-form'
    else:
        filename = 'test-pdf-14-seitig'
    filename += '_%s_%04d.png' % (zoom, bigpage)

    filepath = os.path.join(settings.MEDIA_ROOT, 'mediaserver', 'images', filename)
    image_data = open(filepath, 'r').read()
    expires = email.utils.formatdate(time.time() + 30 * 24 * 3600, usegmt=True)
    last_modified = email.utils.formatdate(os.path.getmtime(filepath), usegmt=True)
    return (image_data, expires, last_modified)


def get_image(request, id=1, bigpage=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is None!")
    id = int(id)
    bigpage = int(bigpage)

    image_data, expires, last_modified  = get_image_data(id, bigpage, zoom)
    response = HttpResponse(image_data, mimetype='image/png')
    response['Expires'] = expires
    response['Last-Modified'] = last_modified
    response['Cache-Control'] = 'public'
    return response
