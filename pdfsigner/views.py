# -*- coding: utf-8 -*-

import os
import random
import urllib
import urllib2

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.conf import settings

from ecs.utils import forceauth


# TODO check assumption on life-time

class IdStore(object):
    def __init__(self):
        print 'IdStore created'
        self.store = { }

    def __del__(self):
        print 'IdStore deleted'

    def set(self, id, value):
        print 'IdStore: set id "%s", value "%s"' % (id, value)
        if self.store.has_key(id):
                print 'IdStore: error id "%s" already in store' % id
                return 0
        self.store[id] = value
        return 1

    def get(self, id):
        print 'IdStore: get id "%s"' % id
        if self.store.has_key(id) is False:
                print 'IdStore: error id "%s" is not in store' % id
                return None
        return self.store[id]

    def delete(self, id):
        print 'IdStore: delete "%s"' % id
        self.store.pop(id)


id_store = IdStore()


def get_random_id():
    return '%s' % random.randint(1, int(1e17) - 1)


def id_set(id, value=None):
    return id_store.set(id, value)


def id_get(id):
    return id_store.get(id)


def id_delete(id):
    id_store.delete(id)


# TODO BKUApplet - setting background from 
# http://ecsdev.ep3.at:4780/bkuonline/img/chip32.png
# to something ECS branded

def sign(request, pdf_id, pdf_data_size, pdf_name):
    url_sign = '%sSign' % settings.PDFAS_SERVICE
    url_send = request.build_absolute_uri('send')
    url_error = request.build_absolute_uri('error')
    url_receive = request.build_absolute_uri('receive')
    print 'url_sign: "%s"' % url_sign
    print 'url_send: "%s"' % url_send
    print 'url_error: "%s"' % url_error
    print 'url_receive: "%s"' % url_receive
    values = {
        'preview': 'false',
        'connector': 'moc',  # undocumented feature! selects ONLINE CCE/BKU
        'mode': 'binary',
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
    redirect = '%s?%s' % (url_sign, data)
    print 'sign: redirect to [%s]' % redirect
    return HttpResponseRedirect(redirect)


def demo_send_is_authorized(request):
    # TODO think about security implications
    return True


def demo_receive_is_authorized(request):
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
def demo_send(request):
    if demo_send_is_authorized(request) is False:
        return HttpResponseForbidden('<h1>Access denied</h1>')
    if request.REQUEST.has_key('pdf-id'):
        pdf_id = request.REQUEST['pdf-id']
    else:
        return HttpResponseForbidden('<h1>Error: Missing pdf-id</h1>')
    value = id_get(pdf_id)
    if value is None:
        # TODO if too many invalid requests, someone might be trying to guess or brute force the pdf-id
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id</h1>')
    pdf_data, pdf_data_size, pdf_name = demo_get_pdf_data()
    return HttpResponse(pdf_data, mimetype='application/pdf')


@forceauth.exempt
def demo_error(request):
    if request.REQUEST.has_key('error'):
        error = urllib.unquote_plus(request.REQUEST['error'])
    else:
        error = ''
    if request.REQUEST.has_key('cause'):
        cause = urllib.unquote_plus(request.REQUEST['cause'])  # FIXME can't deal with UTF-8 encoded Umlauts
    else:
        cause = ''
    return HttpResponse('<h1>demo_error: error=[%s], cause=[%s]</h1>' % (error, cause))


@forceauth.exempt
def demo_receive(request, jsessionid=None):
    if demo_receive_is_authorized(request) is False:
        return HttpResponseForbidden('<h1>Access denied</h1>')
    print 'demo_receive: jsessionid="%s"' % jsessionid
    if request.REQUEST.has_key('pdf-url') and request.REQUEST.has_key('pdf-id') and request.REQUEST.has_key('num-bytes') and request.REQUEST.has_key('pdfas-session-id'):
       pdf_url = request.REQUEST['pdf-url']
       pdf_id = request.REQUEST['pdf-id']
       num_bytes = request.REQUEST['num-bytes']
       pdfas_session_id = request.REQUEST['pdfas-session-id']
       url = '%s%s?pdf-id=%s&num-bytes=%s&pdfas-session-id=%s' % (settings.PDFAS_SERVICE, pdf_url, pdf_id, num_bytes, pdfas_session_id)
       id_delete(pdf_id)
       return HttpResponse('<h1>Download your signed PDF</h1><a href="%s">download link</a>' % url)
    return HttpResponse('demo_receive: got [%s]' % request)


def demo_sign(request):
    pdf_data, pdf_data_size, pdf_name = demo_get_pdf_data()
    pdf_id = get_random_id()
    id_set(pdf_id, 'demo')
    return sign(request, pdf_id, pdf_data_size, pdf_name)


def demo(request):
    url = request.build_absolute_uri('sign')
    return HttpResponse('<h1>Start the Online PDF Signing Demo</h1><a href="%s">start link</a>' % url)


