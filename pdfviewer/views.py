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


class ImageSet(object):
    def __init__(self, id):
        if id == 1:
            self.zoom_list = [ '1', '3x3', '5x5' ]
            self.zoom_pages = [ 1, 9, 25 ]
            self.height = 1076
            self.width = 760
            self.images = {
                '1': {
                    1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_512.png' },
                    2: { 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_511.png' },
                },
                '3x3': {
                    1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_512.png' },
                },
                '5x5': {
                    1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_512.png' },
                },
            }
        else:
            self.zoom_list = [ '1' ]
            self.zoom_pages = [ 1 ]
            self.images = [ ]
        self.zooms = len(self.zoom_list)

    def has_zoom(self, zoom):
        return self.zoom_list.count(zoom) > 0

    def get_pages(self, zoom):
        return len(self.images[zoom])

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
    zoom_pages = image_set.zoom_pages[zoom_index]
    zoom_pages_neg = -zoom_pages

    pages = image_set.get_pages('1')
    if pages == 0:
        return HttpResponse("Error: no pages found for parameter id = '%s'!" % id)

    if page < 1 or page > pages:
        return HttpResponse("Error: no page = '%s' at zoom = '%s'!" % (page, zoom))

    prev_boundary = zoom_pages
    next_boundary = pages - zoom_pages + 1

    image = image_set.get_image(page, zoom)

    return render(request, 'show.html', {
        'id': id,
        'page': page,
        'pages': pages,
        'zoom': zoom,
        'zoom_index': zoom_index,
        'zoom_pages': zoom_pages,
        'zoom_pages_neg': zoom_pages_neg,
        'prev_boundary': prev_boundary,
        'next_boundary': next_boundary,
        'zoom_list': image_set.zoom_list,
        'zooms': image_set.zooms,
        'height': image_set.height,
        'width': image_set.width,
        'image': image,
    })
