# -*- coding: utf-8 -*-

import email.utils
import time

from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings

from ecs.mediaserver.renderer import Renderer
from ecs.mediaserver.storage import PageData, Storage


def get_image_data(id, bigpage, zoom):
    storage = Storage()
    page_data = storage.load_page(id, bigpage, zoom)
    if page_data is None:
        print 'cache miss, render again ..'
        renderer = Renderer()
        renderer.rerender_bigpage(id, bigpage, zoom)
        page_data = storage.load_page(id, bigpage, zoom)
        if page_data is None:
            print '2nd cache miss, giving up ..'
            return (None, None, None)
    print 'cache hit: loaded %s' % page_data
    png_data = page_data.png_data
    png_time = page_data.png_time
    expires = email.utils.formatdate(time.time() + 30 * 24 * 3600, usegmt=True)
    last_modified = email.utils.formatdate(png_time, usegmt=True)
    return (png_data, expires, last_modified)


def get_image(request, id='1', bigpage=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is None!")
    id = str(id)
    bigpage = int(bigpage)
    image_data, expires, last_modified = get_image_data(id, bigpage, zoom)
    if image_data is None:
        # TODO be more precise: invalid id | can not render image
        return HttpResponseNotFound('<h1>Error: can not fetch Image</h1>')
    response = HttpResponse(image_data, mimetype='image/png')
    response['Expires'] = expires
    response['Last-Modified'] = last_modified
    response['Cache-Control'] = 'public'
    return response
