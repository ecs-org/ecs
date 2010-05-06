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
  

def show(request, id=1, page=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is none!")

    if not is_int(id) or id < 1:
        return HttpResponse("Error: invalid parameter id = '%s'!" % id)
    id = int(id)

    if not is_int(page) or page < 1:
        return HttpResponse("Error: invalid parameter page = '%s'!" % page)
    page = int(page)

    zoom_list = [ '1', '3x3', '5x5' ]
    if zoom_list.count(zoom) < 1:
        return HttpResponse("Error: invalid parameter zoom = '%s'! Choose from %s" % (zoom, zoom_list))
    zoom_index = zoom_list.index(zoom)
    zooms = len(zoom_list)

    images = [
        { 'page': 1, 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_512.png' }, 
        { 'page': 2, 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_511.png' },
    ]
    pages = len(images)
    image = [ image for image in images if image['page'] == page ][0]

    return render(request, 'show.html', {
        'id': id,
        'page': page,
        'pages': pages,
        'zoom': zoom,
        'zoom_list': zoom_list,
        'zoom_index': zoom_index,
        'zooms': zooms,
        'image': image,
    })
