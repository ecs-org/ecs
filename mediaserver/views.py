# -*- coding: utf-8 -*-

import email.utils
import time

from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings

from ecs.documents.models import Document
from ecs.mediaserver.imageset import ImageSet
from ecs.mediaserver.renderer import Renderer
from ecs.mediaserver.storage import Cache, SetData
from ecs.utils import hashauth


def load_refill_set(cache, id):
    try:
        document = Document.objects.get(pk=id)
    except DoesNotExist:
        print 'database miss: document "%s"' % id
        return None
    print 'database hit: loaded document "%s"' % id
    pdf_name = document.file.name
    pages = document.pages
    if pages is None:
        print 'document "%s" was stored without "pages" data' % id
        return None
    set_data = SetData('doc from db', pdf_name, pages)
    if not cache.store_set(id, set_data):
        print 'cache re-fill failed: key "%s", set "%s"' % (cache.get_set_key(id), set_data)
        return None
    else:
        print 'cache re-filled: key "%s", set "%s"' % (cache.get_set_key(id), set_data)
        return set_data


def load_refill_page(cache, id, bigpage, zoom):
    set_data = cache.load_set(id)
    if set_data is None:
        print 'cache miss: key "%s"' % cache.get_set_key(id)
        set_data = load_refill_set(cache, id)
        if set_data is None:
            return None
        else:
            print 'cache hit: loaded key "%s", set "%s"' % (cache.get_set_key(id), set_data)
    if bigpage > set_data.pages or bigpage < 1:
        print 'invalid page "%s"' % bigpage
        return None
    image_set = ImageSet(id, set_data)
    if image_set.render_set.has_zoom(zoom) is False:
        print 'invalid zoom "%s"' % zoom
        return None
    image_set.init_images()
    print 're-render page "%s", zoom "%s"' % (bigpage, zoom)
    renderer = Renderer()
    renderer.render(image_set, True, bigpage, zoom)
    page_data = cache.load_page(id, bigpage, zoom)
    if page_data is None:
        print 'cache re-fill failed: key "%s", page "%s"' % (cache.get_page_key(id, bigpage, zoom), page_data)
    else:
        print 'cache re-filled: key "%s", page "%s"' % (cache.get_page_key(id, bigpage, zoom), page_data)
    return page_data


def get_image_data(id, bigpage, zoom):
    cache = Cache()
    page_data = cache.load_page(id, bigpage, zoom)
    if page_data is None:
        print 'cache miss: key "%s"' % cache.get_page_key(id, bigpage, zoom)
        page_data = load_refill_page(cache, id, bigpage, zoom)
        if page_data is None:
            return (None, None, None)
    else:
        print 'cache hit: key "%s", page "%s"' % (cache.get_page_key(id, bigpage, zoom), page_data)
    png_data = page_data.png_data
    png_time = page_data.png_time
    expires = email.utils.formatdate(time.time() + 30 * 24 * 3600, usegmt=True)
    last_modified = email.utils.formatdate(png_time, usegmt=True)
    return (png_data, expires, last_modified)

@hashauth.protect(ttl=10)
def get_image(request, id='1', bigpage=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    id = str(id)
    bigpage = int(bigpage)
    image_data, expires, last_modified = get_image_data(id, bigpage, zoom)
    if image_data is None:
        return HttpResponseNotFound('<h1>Error: failed to fetch or create Image</h1>')
    response = HttpResponse(image_data, mimetype='image/png')
    response['Expires'] = expires
    response['Last-Modified'] = last_modified
    response['Cache-Control'] = 'public'
    return response
