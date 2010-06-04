# -*- coding: utf-8 -*-

import email.utils
import time

from django.http import HttpResponse
from django.conf import settings

from ecs.mediaserver.storage import Storage


def get_image_data(id, bigpage, zoom):
    storage = Storage()
    png_name, png_data, png_time = sotrage.load_page(id, bigpage, zoom)
    expires = email.utils.formatdate(time.time() + 30 * 24 * 3600, usegmt=True)
    last_modified = email.utils.formatdate(png_time, usegmt=True)
    return (png_data, expires, last_modified)


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
