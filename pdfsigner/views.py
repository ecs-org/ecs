# -*- coding: utf-8 -*-

import os
import random
import urllib
import urllib2

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.conf import settings

from ecs.utils import forceauth


demo_store = [ ]


def demo_send_pdf_is_authorized(request):
    # TODO think about security implications
    return True


def demo_receive_pdf_is_authorized(request):
    # TODO think about security implications
    return True


def demo_get_pdf_data():
    pdf_name = 'test-pdf-14-seitig.pdf'
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdfsigner', 'images', pdf_name)
    f = open(pdf_path, 'rb')
    pdf_data = f.read()
    f.close()
    pdf_data_size = len(pdf_data)
    return pdf_data, pdf_data_size, pdf_name


@forceauth.exempt     
def demo_send_pdf(request):
    if demo_send_pdf_is_authorized(request) is False:
        return HttpResponseForbidden('<h1>Access denied</h1>')
    if request.REQUEST.has_key('pdf-id'):
        pdf_id = request.REQUEST['pdf-id']
    else:
        return HttpResponseForbidden('<h1>Error: Missing pdf-id</h1>')
    try:
        demo_store.remove(pdf_id)
    except ValueError:
        # TODO if too many invalid requests, someone might be trying to guess or brute force the pdf-id
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id</h1>')
    pdf_data, pdf_data_size, pdf_name = demo_get_pdf_data()
    return HttpResponse(pdf_data, mimetype='application/pdf')


@forceauth.exempt
def demo_sign_pdf_error(request):
    if request.REQUEST.has_key('error'):
        error = urllib.unquote_plus(request.REQUEST['error'])
    else:
        error = ''
    if request.REQUEST.has_key('cause'):
        cause = urllib.unquote_plus(request.REQUEST['cause'])  # FIXME can't deal with UTF-8 encoded Umlauts
    else:
        cause = ''
    return HttpResponse('<h1>demo_sign_pdf_error: error=[%s], cause=[%s]</h1>' % (error, cause))


@forceauth.exempt
def demo_receive_pdf(request, jsessionid=''):
    if demo_receive_pdf_is_authorized(request) is False:
        return HttpResponseForbidden('<h1>Access denied</h1>')
    print 'demo_receive_pdf jsessionid="%s"' % jsessionid
    if request.REQUEST.has_key('pdf-url') and request.REQUEST.has_key('pdf-id') and request.REQUEST.has_key('num-bytes') and request.REQUEST.has_key('pdfas-session-id'):
       pdf_url = request.REQUEST['pdf-url']
       pdf_id = request.REQUEST['pdf-id']
       num_bytes = request.REQUEST['num-bytes']
       pdfas_session_id = request.REQUEST['pdfas-session-id']
       url = '%s%s?pdf-id=%s&num-bytes=%s&pdfas-session-id=%s' % (settings.PDFAS_SERVICE, pdf_url, pdf_id, num_bytes, pdfas_session_id)
       return HttpResponse('<h1>Download your signed PDF</h1><a href="%s">download link</a>' % url)
    return HttpResponse('demo_receive_pdf got [%s]' % request)


def demo_sign_pdf(request):
    pdf_data , pdf_data_size, pdf_name = demo_get_pdf_data()
    url_sign = '%sSign' % settings.PDFAS_SERVICE
    pdf_id = '%s' % random.randint(1, 10e17)
    demo_store.append(pdf_id)
    url_send = request.build_absolute_uri('demo_send_pdf')
    url_receive = request.build_absolute_uri('demo_receive_pdf')
    url_error = request.build_absolute_uri('demo_sign_pdf_error')
    values = {
        'preview': 'false',
        'connector': 'moc',  # undocumented feature! selects ONLINE CCE/BKU
        'mode': 'textual',
        'sig_type': 'SIGNATURBLOCK_DE',
        'inline': 'false',
        'filename': pdf_name,
        'num-bytes': '%s' % pdf_data_size,
        'pdf-url': url_send,
        'pdf-id': pdf_id,
        'invoke-app-url': url_receive, 
        'invoke-app-error-url': url_error,
        # session-id=9085B85B364BEC31E7D38047FE54577D
        'locale': 'de',
    }
    data = urllib.urlencode(values)
    print "data:", data
    redirect = '%s?%s' % (url_sign, data)
    print 'demo_sign_pdf: redirect to [%s]' % redirect
    return HttpResponseRedirect(redirect)


def demo(request):
    url = request.build_absolute_uri('demo_sign_pdf')
    return HttpResponse('<h1>Start the Online PDF Signing Demo</h1><a href="%s">start link</a>' % url)
