# -*- coding: utf-8 -*-

import os
import datetime
import tempfile
import urllib
import urllib2

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse, get_callable
from django.core.files.base import File
from django.views.decorators.csrf import csrf_exempt

from ecs.documents.models import Document, DocumentType

from ecs.utils import forceauth
from ecs.utils.pdfutils import pdf_barcodestamp

from .utils import SigningDepot



def sign(request, sign_dict):
    '''
    takes a sign_dict, optionaly stamps pdf_data, signs content, upload it to documents and redirect to redirect_view 
    '''
    t_in = tempfile.NamedTemporaryFile(prefix='sign_', suffix='.pdf', delete=False)
    t_out = tempfile.NamedTemporaryFile(prefix='sign_stamped_', suffix='.pdf', delete=False)
    t_in.write(sign_dict['pdf_data'])
    t_in.seek(0)
    if sign_dict['document_stamp']:
        pdf_barcodestamp(t_in, t_out, sign_dict['document_uuid'])
    else:
        t_out.write(t_in.read())
    t_in.close()
    os.remove(t_in.name)
    
    t_out.seek(0)
    pdf_data_stamped = t_out.read()
    t_out.close()
    os.remove(t_out.name)
    
    sign_dict['pdf_data'] = pdf_data_stamped
    pdf_data_stamped_size = len(pdf_data_stamped)
    pdf_id = SigningDepot().deposit(sign_dict)
    
    PDFAS_SERVICE = "" if not hasattr(settings, 'PDFAS_SERVICE') else settings.PDFAS_SERVICE 
    
    url_sign = '%sSign' % PDFAS_SERVICE
    url_send = request.build_absolute_uri('send')
    url_error = request.build_absolute_uri('error')
    url_receive = request.build_absolute_uri('receive')
    url_preview = request.build_absolute_uri('preview')
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
        'filename': sign_dict['document_filename'],
        'num-bytes': '%s' % pdf_data_stamped_size,
        'pdf-url': url_send,
        'pdf-id': pdf_id,
        'invoke-app-url': url_receive, 
        'invoke-preview-url': url_preview,
        # session-id=9085B85B364BEC31E7D38047FE54577D, not used
        'locale': 'de',
    }
    data = urllib.urlencode(values)
    redirect = '%s?%s' % (url_sign, data)
    print 'sign: redirect to [%s]' % redirect

    if (not PDFAS_SERVICE or PDFAS_SERVICE == "mock:"):
        # we mock calling the applet, and directly go to sign_receive, to make automatic tests possible
        fakeget = request.GET.copy() 
        fakeget['pdf-id'] = pdf_id # inject pdf-id for mock
        request.GET = fakeget
        pdf_data = sign_send(request).content
        assert SigningDepot().get(request.REQUEST['pdf-id']), pdf_data
        fakeget['pdfas-session-id'] = 'mock_pdf_as' # inject pdfas-session-id
        fakeget['pdf-url'] = url_send
        fakeget['num-bytes'] = pdf_data_stamped_size  
        request.GET = fakeget
        
        return sign_receive(request)
    else:
        return HttpResponseRedirect(redirect)


@csrf_exempt
@forceauth.exempt
def sign_error(request):
    '''
    to be directly accessed by pdf-as so it can report errors. 
     * needs @csrf_exempt to ignore missing csrf token.
     * needs @forceauth.exempt because pdf-as can't authenticate.
    '''
    if request.REQUEST.has_key('pdf-id'):
        SigningDepot().pop(request.REQUEST['pdf-id'])
        
    if request.REQUEST.has_key('error'):
        error = urllib.unquote_plus(request.REQUEST['error'])
    else:
        error = ''
    if request.REQUEST.has_key('cause'):
        cause = urllib.unquote_plus(request.REQUEST['cause'])  # FIXME can't deal with UTF-8 encoded Umlauts
    else:
        cause = ''
    # no pdf id, no explicit cleaning possible
    return HttpResponse('<h1>sign_error: error=[%s], cause=[%s]</h1>' % (error, cause))


@csrf_exempt
@forceauth.exempt
def sign_send(request, jsessionid=None):
    '''
    to be directly accessed by pdf-as so it can retrieve the pdf to sign
     * needs @csrf_exempt to ignore missing csrf token.
     * needs @forceauth.exempt because pdf-as can't authenticate.
    '''
    sign_dict = SigningDepot().get(request.REQUEST['pdf-id'])
    if sign_dict is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')
    
    return HttpResponse(sign_dict["pdf_data"], mimetype='application/pdf')


@csrf_exempt
@forceauth.exempt
def sign_preview(request, jsessionid=None):
    '''
    to be directly accessed by pdf-as so it can show a preview of the to be signed pdf on the applet page.
     * needs @csrf_exempt to ignore missing csrf token.
     * needs @forceauth.exempt because pdf-as can't authenticate.
    '''
    sign_dict = SigningDepot().get(request.REQUEST['pdf-id'])
    if sign_dict is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')
    
    return HttpResponse(sign_dict["html_preview"])


@csrf_exempt
@forceauth.exempt
def sign_receive_landing(request, jsessionid=None):
    '''
    to be directly accessed by pdf-as so it can bump ecs to download the signed pdf.
    current version of pdf-as has some bug, to include jsessionid as part of the url,
    working around with landing page
     * needs @csrf_exempt to ignore missing csrf token.
     * needs @forceauth.exempt because pdf-as can't authenticate.
    '''
    return sign_receive(request, jsessionid);


def sign_receive(request, jsessionid=None):
    '''
    to be accessed by pdf-as so it can bump ecs to download the signed pdf.
    called by the sign_receive_landing view, to workaround some pdf-as issues
    '''
    
    PDFAS_SERVICE = "" if not hasattr(settings, 'PDFAS_SERVICE') else settings.PDFAS_SERVICE 
    
    if (request.REQUEST.has_key('pdf-url') and 
        request.REQUEST.has_key('pdf-id') and 
        request.REQUEST.has_key('num-bytes') and 
        request.REQUEST.has_key('pdfas-session-id')):
        
        pdf_url = request.REQUEST['pdf-url']
        pdf_id = request.REQUEST['pdf-id']
        num_bytes = int(request.REQUEST['num-bytes'])
        pdfas_session_id = request.REQUEST['pdfas-session-id']
        url = '%s%s?pdf-id=%s&num-bytes=%s&pdfas-session-id=%s' % (PDFAS_SERVICE, pdf_url, pdf_id, num_bytes, pdfas_session_id)
        sign_dict = SigningDepot().pop(pdf_id)
        
        if sign_dict is None:
            return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')

        t_pdfas = tempfile.NamedTemporaryFile(prefix='sign_', suffix='.pdf', delete=False)
        
        if (not PDFAS_SERVICE or PDFAS_SERVICE == "mock:"): 
            t_pdfas.write(sign_dict['pdf_data'])
        else:     
            # f_pdfas is not seekable, so we have to store it as local file first
            sock_pdfas = urllib2.urlopen(url)
            t_pdfas.write(sock_pdfas.read(num_bytes))
            sock_pdfas.close()
        
        d = datetime.datetime.now()
        parent_obj = get_object_or_404(get_callable(sign_dict['parent_name']), pk=sign_dict['parent_pk'])
        doctype, created = DocumentType.objects.get_or_create(identifier= sign_dict['document_identifier'])
        document = Document.objects.create(uuid_document=sign_dict["document_uuid"], 
            parent_object=parent_obj, branding='n', doctype=doctype, file=File(t_pdfas),
            original_file_name=sign_dict["document_filename"], date=d)
        t_pdfas.close()
        os.remove(t_pdfas.name)
        
        return HttpResponseRedirect(reverse(sign_dict['redirect_view'], kwargs={'document_pk': document.pk}))
    else:
        return HttpResponse('sign_receive: got [%s]' % request)

