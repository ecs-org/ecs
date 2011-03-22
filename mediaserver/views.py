# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.utils.translation import ugettext as _

from ecs.utils import forceauth
from ecs.utils.s3utils import S3url
from ecs.utils.pdfutils import Page

from ecs.mediaserver.mediaprovider import MediaProvider

@forceauth.exempt
def prime_cache(request, uuid):
    s3url = S3url(settings.MS_CLIENT ["key_id"], settings.MS_CLIENT ["key_secret"])
    if not s3url.verifyUrlString(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))

    mediaprovider = MediaProvider()
    mediaprovider.renderPages(uuid)

    return HttpResponse('ok')

@forceauth.exempt
def get_page(request, uuid, tiles_x, tiles_y, width, pagenr):
    s3url = S3url(settings.MS_CLIENT ["key_id"], settings.MS_CLIENT ["key_secret"])
    if not s3url.verifyUrlString(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))
    
    mediaprovider = MediaProvider()
    try:
        f = mediaprovider.getPage(Page(uuid, tiles_x, tiles_y, width, pagenr))
    except KeyError:
        return HttpResponseNotFound()
    
    data = f.read() if hasattr(f, 'read') else f
    return HttpResponse(data, mimetype='image/png')
        
@forceauth.exempt
def get_blob(request, uuid, filename, mimetype='application/pdf', branding=None):
    s3url = S3url(settings.MS_CLIENT['key_id'], settings.MS_CLIENT['key_secret'])
    if not s3url.verifyUrlString(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))

    mediaprovider = MediaProvider()
    try:
        f = mediaprovider.getBlob(uuid)
    except KeyError:
        return HttpResponseNotFound()

    #fixme: brand pdf with uuid barcode, and if branding != none with branding barcode also

    response = HttpResponse(f.read(), mimetype=mimetype)
    response['Content-Disposition'] = 'attachment;filename=%s' % (filename)
    return response  

@forceauth.exempt
def get_pdf(request, *args, **kwargs):
    kwargs['mimetype'] = 'application/pdf'
    return get_blob(request, *args, **kwargs)

@forceauth.exempt
def prepare_branded(request, uuid, mimetype='application/pdf', brandprepare=True):
    return prepare(request, uuid, mimetype, brandprepare)

@forceauth.exempt
def prepare(request, uuid, mimetype='application/pdf', brandprepare=False):
    return HttpResponseBadRequest(_("sorry, unfinished"))


