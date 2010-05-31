# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from json import JSONEncoder

from ecs.core.views.utils import render, redirect_to_next_url


def is_int(x):
    try:
        i = int(x)
        return True
    except:
        return False


class ImageSet(object):
    def __init__(self, id):
        if id == 1:
            self.zoom_list = [ '1', '3x3', '5x5' ]
            self.zoom_pages = [ [1,1], [3,3], [5,5] ]
            self.width = 760
            self.height = 1076
            self.images = {
                '1': {
                     1: { 'url': '/mediaserver/1/1/1/' },
                     2: { 'url': '/mediaserver/1/2/1/' },
                     3: { 'url': '/mediaserver/1/3/1/' },
                     4: { 'url': '/mediaserver/1/4/1/' },
                     5: { 'url': '/mediaserver/1/5/1/' },
                     6: { 'url': '/mediaserver/1/6/1/' },
                     7: { 'url': '/mediaserver/1/7/1/' },
                     8: { 'url': '/mediaserver/1/8/1/' },
                     9: { 'url': '/mediaserver/1/9/1/' },
                    10: { 'url': '/mediaserver/1/10/1/' },
                    11: { 'url': '/mediaserver/1/11/1/' },
                    12: { 'url': '/mediaserver/1/12/1/' },
                    13: { 'url': '/mediaserver/1/13/1/' },
                    14: { 'url': '/mediaserver/1/14/1/' },
                    15: { 'url': '/mediaserver/1/15/1/' },
                    16: { 'url': '/mediaserver/1/16/1/' },
                    17: { 'url': '/mediaserver/1/17/1/' },
                    18: { 'url': '/mediaserver/1/18/1/' },
                },
                '3x3': {
                     1: { 'url': '/mediaserver/1/1/3x3/' },
                     2: { 'url': '/mediaserver/1/2/3x3/' },
                },
                '5x5': {
                     1: { 'url': '/mediaserver/1/1/5x5/' },
                },
            }
        else:
            self.zoom_list = [ '1', '3x3', '5x5' ]
            self.zoom_pages = [ [1,1], [3,3], [5,5] ]
            self.width = 800
            self.height = 1131
            self.images = {
                '1': {
                     1: { 'url': '/mediaserver/2/1/1/' },
                     2: { 'url': '/mediaserver/2/2/1/' },
                     3: { 'url': '/mediaserver/2/3/1/' },
                     4: { 'url': '/mediaserver/2/4/1/' },
                     5: { 'url': '/mediaserver/2/5/1/' },
                     6: { 'url': '/mediaserver/2/6/1/' },
                     7: { 'url': '/mediaserver/2/7/1/' },
                     8: { 'url': '/mediaserver/2/8/1/' },
                     9: { 'url': '/mediaserver/2/9/1/' },
                    10: { 'url': '/mediaserver/2/10/1/' },
                    11: { 'url': '/mediaserver/2/11/1/' },
                    12: { 'url': '/mediaserver/2/12/1/' },
                    13: { 'url': '/mediaserver/2/13/1/' },
                    14: { 'url': '/mediaserver/2/14/1/' },
                },
                '3x3': {
                     1: { 'url': '/mediaserver/2/1/3x3/' },
                     2: { 'url': '/mediaserver/2/2/3x3/' },
                },
                '5x5': {
                     1: { 'url': '/mediaserver/2/1/5x5/' },
                },
            }
        self.zooms = len(self.zoom_list)

    def has_zoom(self, zoom):
        return self.zoom_list.count(zoom) > 0

    def get_pages(self):
        return len(self.images['1'])

    def get_image(self, page, zoom):
        images = self.images[zoom]
        return images[page]


def show(request, id=1, page=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is none!")

    if not is_int(id) or (id < 1):
        return HttpResponse("Error: invalid parameter id = '%s'!" % id)
    id = int(id)

    if not is_int(page):
        return HttpResponse("Error: invalid parameter page = '%s'!" % page)
    page = int(page)

    image_set = ImageSet(id)

    if not image_set.has_zoom(zoom):
        return HttpResponse("Error: invalid parameter zoom = '%s'! Choose from %s" % (zoom, image_set.zoom_list))
    zoom_index = image_set.zoom_list.index(zoom)
    zoom_list = JSONEncoder().encode(image_set.zoom_list);
    zoom_pages = JSONEncoder().encode(image_set.zoom_pages);

    pages = image_set.get_pages()
    if pages == 0:
        return HttpResponse("Error: no pages found for parameter id = '%s'!" % id)

    if page < 1 or page > pages:
        return HttpResponse("Error: no page = '%s' at zoom = '%s'!" % (page, zoom))

    images = JSONEncoder().encode(image_set.images)

    return render(request, 'show.html', {
        'id': id,
        'page': page,
        'pages': pages,
        'zoom_index': zoom_index,
        'zoom_list': zoom_list,
        'zoom_pages': zoom_pages,
        'height': image_set.height,
        'width': image_set.width,
        'images': images,
    })


def demo(request):
    return render(request, 'demo.html', {})

