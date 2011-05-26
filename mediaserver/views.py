# -*- coding: utf-8 -*-
from tempfile import NamedTemporaryFile
from logging import getLogger

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.utils.translation import ugettext as _

from ecs.utils import forceauth
from ecs.utils.s3utils import S3url
from ecs.utils.pdfutils import Page, pdf_barcodestamp

from ecs.mediaserver.utils import MediaProvider


@forceauth.exempt
def prime_cache(request, uuid, mimetype='application/pdf'):
    s3url = S3url(settings.MS_CLIENT ["key_id"], settings.MS_CLIENT ["key_secret"])
    if not s3url.verifyUrlString(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))

    mediaprovider = MediaProvider()
    mediaprovider.prime_blob(uuid, mimetype, wait=False)
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
def get_pdf(request, *args, **kwargs):
    kwargs['mimetype'] = 'application/pdf'
    return get_blob(request, *args, **kwargs)


@forceauth.exempt
def get_blob(request, uuid, filename, mimetype='application/pdf', branding=None):
    logger = getLogger()
    s3url = S3url(settings.MS_CLIENT['key_id'], settings.MS_CLIENT['key_secret'])
    if not s3url.verifyUrlString(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))

    mediaprovider = MediaProvider()
    if branding is not None:
        # TODO: look if branding is not "True" and use it as second stamp 
        try:
            f = mediaprovider.getBlob(uuid+uuid, try_vault=False)
        except KeyError:
            try:
                inputpdf = mediaprovider.getBlob(uuid)
            except KeyError:
                return HttpResponseNotFound()
            
            with NamedTemporaryFile(suffix='.pdf') as outputpdf:
                pdf_barcodestamp(inputpdf, outputpdf, uuid)
                outputpdf.seek(0)
                logger.info('barcodestamp blob %s' % uuid)
                mediaprovider._cacheBlob(uuid+uuid, outputpdf)
                
            f = mediaprovider.getBlob(uuid+uuid, try_vault=False)
    else:        
        try:
            f = mediaprovider.getBlob(uuid)     
        except KeyError:
            return HttpResponseNotFound()

    response = HttpResponse(f.read(), mimetype=mimetype)
    response['Content-Disposition'] = 'attachment;filename=%s' % (filename)
    return response  

