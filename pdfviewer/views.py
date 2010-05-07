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
            self.height = 1076
            self.width = 760
            self.images = [
                { 'page': 1, 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_512.png' }, 
                { 'page': 2, 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_511.png' },
            ]
        else:
            self.zoom_list = [ '1' ]
            self.images = []
        self.zooms = len(self.zoom_list)
        self.pages = len(self.images)

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

    image_set = ImageSet(id)
    if image_set.pages < 1:
        return HttpResponse("Error: no pages found for parameter id = '%s'!" % id)

    if not is_int(page):
        return HttpResponse("Error: invalid parameter page = '%s'!" % page)
    page = int(page)
    if page < 1 or page > image_set.pages:
        return HttpResponse("Error: invalid parameter page = '%s'!" % page)

    if image_set.zoom_list.count(zoom) < 1:
        return HttpResponse("Error: invalid parameter zoom = '%s'! Choose from %s" % (zoom, image_set.zoom_list))
    zoom_index = image_set.zoom_list.index(zoom)

    for i in image_set.images:
        if i['page'] == page:
            image = i
            break

    return render(request, 'show.html', {
        'id': id,
        'page': page,
        'zoom': zoom,
        'zoom_index': zoom_index,
        'zoom_list': image_set.zoom_list,
        'zooms': image_set.zooms,
        'pages': image_set.pages,
        'height': image_set.height,
        'width': image_set.width,
        'image': image,
    })
