# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from json import JSONEncoder, JSONDecoder

from ecs.core.views.utils import render, redirect_to_next_url


from ecs.core.models import Document
from ecs.mediaserver.imageset import ImageSet
from ecs.mediaserver.storage import Cache, SetData

from ecs.pdfviewer.models import Annotation

def load_refill_set(id):
    try:
        document = Document.objects.get(pk=id)
    except Document.DoesNotExist:
        print 'database miss: document "%s"' % id
        return None
    print 'database hit: loaded document "%s"' % id
    pdf_name = document.file.name
    pages = document.pages
    if pages is None:
        print 'document "%s" was stored without "pages" data' % id
        return None
    set_data = SetData('doc from db', pdf_name, pages)
    cache = Cache()
    if not cache.store_set(id, set_data):
        print 'cache re-fill failed: key "%s", set "%s"' % (cache.get_set_key(id), set_data)
        return None
    else:
        print 'cache re-filled: key "%s", set "%s"' % (cache.get_set_key(id), set_data)
        return set_data


def show(request, id='1', page=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse('Error: you need to be logged in!')
    else:
        user = request.user
        if user is None:
            return HttpResponse('Error: user is None!')

    id = str(id)
    page = int(page)

    image_set = ImageSet(id)
    if image_set.load() is False:
        image_set.set_data = load_refill_set(id)
        if image_set.set_data is None:
            return HttpResponse('Error: can not load ImageSet "%s"!' % id)
        image_set.init_images()
    render_set = image_set.render_set
    if not render_set.has_zoom(zoom):
        return HttpResponse('Error: invalid parameter zoom = "%s"! Choose from %s' % (zoom, render_set.zoom_list))
    zoom_index = render_set.zoom_list.index(zoom)
    zoom_list_json = JSONEncoder().encode(render_set.zoom_list);
    zoom_pages_json = JSONEncoder().encode(render_set.zoom_pages);

    pages = image_set.set_data.pages

    if page < 1 or page > pages:
        return HttpResponse('Error: no page = "%s" at zoom = "%s"!' % (page, zoom))

    images_json = JSONEncoder().encode(image_set.images)

    annotations = dict([(anno.uuid, JSONDecoder().decode(anno.layoutData)) for anno in Annotation.objects.filter(docid=id, page=page)])
    
    allAnno = JSONEncoder().encode(annotations)

    return render(request, 'pdfviewer/show.html', {
        'id': id,
        'allAnno': allAnno,
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

def annotation(request, did, page, zoom):
    if not request.POST:
        return HttpResponse('POST only')
        
    print did, page, zoom, request.POST
    anno = Annotation(uuid=request.POST['uuid'])
    anno.layoutData = request.POST['layoutData']
    anno.docid = Document.objects.get(id=did);
    anno.page = page;
    anno.save()
    return HttpResponse('OK')

def delete_annotation(request, did, page, zoom):
    if not request.POST:
        return HttpResponse('POST only')
        
    print did, page, zoom, request.POST
    anno = Annotation.objects.filter(uuid=request.POST['uuid']).delete()
    return HttpResponse('OK')