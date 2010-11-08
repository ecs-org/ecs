# -*- coding: utf-8 -*-

from uuid import UUID

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest

from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.cacheobjects import MediaBlob, Docshot

from ecs.utils.s3utils import S3url
from ecs.utils import forceauth


@forceauth.exempt
def docshot(request, uuid, tiles_x, tiles_y, width, pagenr):
    s3url = S3url(settings.MS_CLIENT ["key_id"], settings.MS_CLIENT ["key_secret"])
    if not s3url.verifyUrlString(request.get_full_path()):
        return HttpResponseBadRequest("Invalid expiring url");
    
    docprovider = DocumentProvider()    
    f = docprovider.getDocshot(Docshot(MediaBlob(UUID(uuid)), tiles_x, tiles_y, width, pagenr))

    if not f:
        return HttpResponseNotFound()
    
    data = f.read() if hasattr(f, 'read') else f
    return HttpResponse(f, mimetype='image/png')
        
@forceauth.exempt
def download_pdf(request, uuid, mimetype= "application/pdf"):
    s3url = S3url(settings.MS_CLIENT ["key_id"], settings.MS_CLIENT ["key_secret"])
    if not s3url.verifyUrlString(request.get_full_path()):
        return HttpResponseBadRequest("Invalid expiring url");
    
    docprovider = DocumentProvider() 
    f = docprovider.getBlob(MediaBlob(UUID(uuid)))

    if f:
        return HttpResponse(f.read(), mimetype=mimetype) 
    else:
        return HttpResponseNotFound()
    
