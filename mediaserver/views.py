# -*- coding: utf-8 -*-

from uuid import UUID

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest

from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.cacheobjects import MediaBlob, Docshot

from ecs.utils import s3utils
from ecs.utils import forceauth


@forceauth.exempt
def docshot(request, uuid, tiles_x, tiles_y, width, pagenr):
    if not s3utils.verifyExpiringUrlString(request.get_full_path()):
        return HttpResponseBadRequest("Invalid expiring url");

    docprovider = DocumentProvider()    
    f = docprovider.getDocshot(Docshot(MediaBlob(UUID(uuid)), tiles_x, tiles_y, width, pagenr))

    if not f:
        return HttpResponseNotFound()
    if hasattr(f, 'read'):
        f = f.read()
    return HttpResponse(f, mimetype='image/png')
        

def download_pdf(request, uuid):
    key_id = settings.MS_CLIENT ["key_id"]
    key_secret = settings.MS_CLIENT ["key_secret"]
    if not s3utils.s3url(key_id, key_secret).verifyUrlString(request.get_full_path()):
        return HttpResponseBadRequest("Invalid expiring url");
    
    docprovider = DocumentProvider() 
    f = docprovider.getBlob(MediaBlob(UUID(uuid)))

    if f:
        return HttpResponse(f.read(), mimetype='application/pdf') # FIXME: view name and mimetype is wrong, mimetype will be most of the time pdf, but not always
    else:
        return HttpResponseNotFound()
    
