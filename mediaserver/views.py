# -*- coding: utf-8 -*-
from logging import getLogger

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.utils.translation import ugettext as _

from ecs.utils import forceauth
from ecs.utils.pdfutils import Page
from ecs.mediaserver.utils import MediaProvider, AuthUrl


@forceauth.exempt
def prime_cache(request, uuid, mimetype='application/pdf'):
    authurl = AuthUrl(settings.MS_CLIENT ["key_id"], settings.MS_CLIENT ["key_secret"])
    if not authurl.verify(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))

    mediaprovider = MediaProvider()
    mediaprovider.prime_blob(uuid, mimetype, wait=False)
    return HttpResponse('ok')


@forceauth.exempt
def get_page(request, uuid, tiles_x, tiles_y, width, pagenr):
    authurl = AuthUrl(settings.MS_CLIENT ["key_id"], settings.MS_CLIENT ["key_secret"])
    if not authurl.verify(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))
    
    mediaprovider = MediaProvider()
    try:
        f = mediaprovider.get_page(Page(uuid, tiles_x, tiles_y, width, pagenr))
    except KeyError:
        return HttpResponseNotFound()
    
    data = f.read() if hasattr(f, 'read') else f
    return HttpResponse(data, mimetype='image/png')
        

@forceauth.exempt
def get_pdf(request, uuid, filename, branding):
    return get_blob(request, uuid, filename, mimetype='application/pdf', branding=branding)


@forceauth.exempt
def get_blob(request, uuid, filename, mimetype='application/pdf', branding=None):
    logger = getLogger()
    authurl = AuthUrl(settings.MS_CLIENT['key_id'], settings.MS_CLIENT['key_secret'])
    
    if not authurl.verify(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))

    f = None
    mediaprovider = MediaProvider()
    try:    
        try:
            if branding is not None:                
                f = mediaprovider.get_branded(uuid, mimetype, True)
            else:        
                f = mediaprovider.get_blob(uuid)
        except KeyError:
            return HttpResponseNotFound()
            
        response = HttpResponse(f.read(), mimetype=mimetype)
        response['Content-Disposition'] = 'attachment;filename=%s' % (filename)
    finally:
        if hasattr(f, "close"):
            f.close()
    
    return response  

