# -*- coding: utf-8 -*-

import email.utils
import os
import time
import urllib
import urllib2

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.conf import settings

from ecs.mediaserver.storage import PageData, Storage
from ecs.utils import forceauth


def get_image_data(id, bigpage, zoom):
    storage = Storage()
    page_data = storage.load_page(id, bigpage, zoom)
    if page_data is None:
        print 'cache miss'
        return (None, None, None)
    print 'cache hit: loaded %s' % page_data
    png_data = page_data.png_data
    png_time = page_data.png_time
    expires = email.utils.formatdate(time.time() + 30 * 24 * 3600, usegmt=True)
    last_modified = email.utils.formatdate(png_time, usegmt=True)
    return (png_data, expires, last_modified)


def get_image(request, id=1, bigpage=1, zoom='1'):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is None!")
    id = int(id)
    bigpage = int(bigpage)
    image_data, expires, last_modified = get_image_data(id, bigpage, zoom)
    if image_data is None:
        return HttpResponseNotFound('<h1>Image not found in storage</h1>')
    response = HttpResponse(image_data, mimetype='image/png')
    response['Expires'] = expires
    response['Last-Modified'] = last_modified
    response['Cache-Control'] = 'public'
    return response


def send_pdf_is_authorized(request):
    # TODO think about security implications
    return True


def receive_pdf_is_authorized(request):
    # TODO think about security implications
    return True


def get_pdf_data():
    #pdf_name = 'Bericht.pdf'
    pdf_name = 'test-pdf-14-seitig.pdf'
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'mediaserver', 'images', pdf_name)
    f = open(pdf_path, 'rb')
    pdf_data = f.read()
    f.close()
    pdf_data_size = len(pdf_data)
    return pdf_data, pdf_data_size, pdf_name


@forceauth.exempt     
def send_pdf(request):
    if send_pdf_is_authorized(request) is False:
        return HttpResponseForbidden('<h1>Access denied</h1>')
    pdf_data, pdf_data_size, pdf_name = get_pdf_data()
    response = HttpResponse(pdf_data, mimetype='application/pdf')
    return response


@forceauth.exempt
def sign_pdf_error(request):
    if request.REQUEST.has_key('error'):
        error = urllib.unquote_plus(request.REQUEST['error'])
    else:
        error = ''
    if request.REQUEST.has_key('cause'):
        cause = urllib.unquote_plus(request.REQUEST['cause'])  # FIXME can't deal with UTF-8 encoded Umlauts
    else:
        cause = ''
    return HttpResponse(u'signpdf: error=[%s], cause=[%s]' % (error, cause))


@forceauth.exempt
def receive_pdf(request):
    if receive_pdf_is_authorized(request) is False:
        return HttpResponseForbidden('<h1>Access denied</h1>')
    # ..
    return HttpResponse('receive signed PDF got [%s]' % request)


def sign_pdf(request):
    pdf_data , pdf_data_size, pdf_name = get_pdf_data()
    url = 'http://advancedcode.de:8180/pdf-as/Sign'
    values = {
        'preview': 'false',
        'connector': 'bku',
        'mode': 'textual',
        'sig_type': 'SIGNATURBLOCK_DE',
        'inline': 'false',
        'filename': pdf_name,
        'num-bytes': '%s' % pdf_data_size,
        'pdf-url': request.build_absolute_uri('/mediaserver/sendpdf'), 
        'pdf-id': '1956507909008215134',
        'invoke-app-url': request.build_absolute_uri('/mediaserver/receivepdf'),
        'invoke-app-error-url': request.build_absolute_uri('/mediaserver/signpdferror'),
        # session-id=9085B85B364BEC31E7D38047FE54577D
        'locale': 'de',
    }
    data = urllib.urlencode(values)
    redirect = '%s?%s' % (url, data)
    print 'redirect to [%s]' % redirect
    return HttpResponseRedirect(redirect)
