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
                    1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_51_0002.png' },
                    2: { 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_51_0001.png' },
                },
                '3x3': {
                    1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_51_0002.png' },
                },
                '5x5': {
                    1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/Meld_51_0002.png' },
                },
            }
        elif id == 2:
            self.zoom_list = [ '1', '3x3', '5x5' ]
            self.zoom_pages = [ [1,1], [3,3], [5,5] ]
            self.width = 760
            self.height = 1076
            self.images = {
                '1': {
                     1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0001.png' },
                     2: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0002.png' },
                     3: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0003.png' },
                     4: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0004.png' },
                     5: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0005.png' },
                     6: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0006.png' },
                     7: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0007.png' },
                     8: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0008.png' },
                     9: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0009.png' },
                    10: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0010.png' },
                    11: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0011.png' },
                    12: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0012.png' },
                    13: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0013.png' },
                    14: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0014.png' },
                    15: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0015.png' },
                    16: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0016.png' },
                    17: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0017.png' },
                    18: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_0018.png' },
                },
                '3x3': {
                     1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_3x3_0001.png' },
                     2: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_3x3_0002.png' },
                },
                '5x5': {
                     1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/ecs-09-submission-form_5x5_0001.png' },
                },
            }
        elif id == 3:
            self.zoom_list = [ '1', '3x3', '5x5' ]
            self.zoom_pages = [ [1,1], [3,3], [5,5] ]
            self.width = 800
            self.height = 1131
            self.images = {
                '1': {
                     1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0001.png' },
                     2: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0002.png' },
                     3: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0003.png' },
                     4: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0004.png' },
                     5: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0005.png' },
                     6: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0006.png' },
                     7: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0007.png' },
                     8: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0008.png' },
                     9: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0009.png' },
                    10: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0010.png' },
                    11: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0011.png' },
                    12: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0012.png' },
                    13: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0013.png' },
                    14: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_0014.png' },
                },
                '3x3': {
                     1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_3x3_0001.png' },
                     2: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_3x3_0002.png' },
                },
                '5x5': {
                     1: { 'url': settings.MEDIA_URL + 'pdfviewer/images/test-pdf-14-seitig_5x5_0001.png' },
                },
            }
        else:
            self.zoom_list = [ '1' ]
            self.zoom_pages = [ [1,1] ]
            self.images = [ ]
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

