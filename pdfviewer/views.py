# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from json import JSONEncoder

from ecs.core.views.utils import render, redirect_to_next_url

from ecs.mediaserver.imageset import ImageSet


def show(request, id=1, page=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is None!")

    id = int(id)
    page = int(page)

    image_set = ImageSet(id)
    render_set = image_set.render_set
    if not render_set.has_zoom(zoom):
        return HttpResponse("Error: invalid parameter zoom = '%s'! Choose from %s" % (zoom, render_set.zoom_list))
    zoom_index = render_set.zoom_list.index(zoom)
    zoom_list_json = JSONEncoder().encode(render_set.zoom_list);
    zoom_pages_json = JSONEncoder().encode(render_set.zoom_pages);

    pages = image_set.pages

    if page < 1 or page > pages:
        return HttpResponse("Error: no page = '%s' at zoom = '%s'!" % (page, zoom))

    images_json = JSONEncoder().encode(image_set.images)

    return render(request, 'pdfviewer/show.html', {
        'id': id,
        'page': page,
        'pages': pages,
        'zoom_index': zoom_index,
        'zoom_list': zoom_list_json,
        'zoom_pages': zoom_pages_json,
        'height': render_set.height,
        'width': render_set.width,
        'images': images_json,
    })


def demo(request):
    return render(request, 'pdfviewer/demo.html', {})

