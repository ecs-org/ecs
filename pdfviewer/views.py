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
  

def show(request, id=1, page=1):
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

    images = [
        { 'page': 1, 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_512.png' }, 
        { 'page': 2, 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_511.png' },
    ]
    pages = len(images)

    thumbs = [
        { 'page': 1, 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_512.png' }, 
        { 'page': 2, 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_511.png' },
    ]

    return render(request, 'show.html', {
        'id': id,
        'page': page,
        'pages': pages,
        'images': images,
        'thumbs': thumbs,
    })
