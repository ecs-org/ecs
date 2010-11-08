# -*- coding: utf-8 -*-

import urllib
from django.conf import settings
from django.http import HttpResponseRedirect

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

