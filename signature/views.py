# -*- coding: utf-8 -*-

import os
from datetime import datetime
from tempfile import NamedTemporaryFile
import urllib
import urllib2
import time

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse, get_callable
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

from ecs.documents.models import Document, DocumentType
from ecs.tasks.models import Task

from ecs.utils import forceauth
from ecs.utils.pdfutils import pdf_barcodestamp
from ecs.signature.utils import SigningDepot


def sign(request, sign_dict):
    '''
    takes a sign_dict, optionally stamps pdf_data, signs content, upload it to documents and redirect to redirect_view 
    '''

    if sign_dict['document_stamp']:
        with NamedTemporaryFile(suffix='.pdf') as tmp_in:
            with NamedTemporaryFile(suffix='.pdf') as tmp_out:
                tmp_in.write(sign_dict['pdf_data'])
                tmp_in.seek(0)
                pdf_barcodestamp(tmp_in, tmp_out, sign_dict['document_uuid'])
                tmp_out.seek(0)
                sign_dict['pdf_data'] = tmp_out.read()

    pdf_data_size = len(sign_dict['pdf_data'])
    pdf_id = SigningDepot().deposit(sign_dict)

    PDFAS_SERVICE = getattr(settings, 'PDFAS_SERVICE', 'mock:')
    
    values = {
        'preview': 'false',
        'connector': 'moc',  # undocumented feature! selects ONLINE CCE/BKU
        'mode': 'binary',
        'sig_type': 'SIGNATURBLOCK_DE',
        'inline': 'false',
        'filename': sign_dict['document_filename'],
        'num-bytes': '%s' % pdf_data_size,
        'pdf-url': request.build_absolute_uri('send'),
        'pdf-id': pdf_id,
        'invoke-app-url': request.build_absolute_uri('receive'),
        'invoke-preview-url': request.build_absolute_uri('preview'),
        # session-id=9085B85B364BEC31E7D38047FE54577D, not used
        'locale': 'de',
    }
    data = urllib.urlencode(dict([k, v.encode('utf-8')] for k, v in values.items()))
    redirect = '{0}Sign?{1}'.format(PDFAS_SERVICE, data)
    #print 'sign: redirect to [%s]' % redirect

    if not PDFAS_SERVICE == 'mock:':
        return HttpResponseRedirect(redirect)

    # we mock calling the applet, and directly go to sign_receive, to make automatic tests possible
    fakeget = request.GET.copy()
    fakeget['pdf-id'] = pdf_id # inject pdf-id for mock
    request.GET = fakeget
    pdf_data = sign_send(request).content
    assert SigningDepot().get(request.REQUEST['pdf-id']), pdf_data
    fakeget['pdfas-session-id'] = 'mock_pdf_as' # inject pdfas-session-id
    fakeget['pdf-url'] = request.build_absolute_uri('send')
    fakeget['num-bytes'] = pdf_data_size
    request.GET = fakeget
    
    return sign_receive(request)

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

    PDFAS_SERVICE = getattr(settings, 'PDFAS_SERVICE', 'mock:')

    q = {}
    for k in ('pdf-url', 'pdf-id', 'num-bytes', 'pdfas-session-id',):
        if not request.REQUEST.has_key(k):
            return HttpResponse('sign_receive: got [%s]' % request)

        q[k] = request.REQUEST[k]

    pdf_url = q.pop('pdf-url')
    url = '{0}{1}?{2}'.format(PDFAS_SERVICE, pdf_url, urllib.urlencode(q))

    sign_dict = SigningDepot().pop(q['pdf-id'])
    if sign_dict is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')

    if not PDFAS_SERVICE == 'mock:':
        sock_pdfas = urllib2.urlopen(url)
        pdf_data = sock_pdfas.read(q['num-bytes'])
    else:
        pdf_data = sign_dict['pdf_data']

    f = ContentFile(pdf_data)
    f.name = 'vote.pdf'

    parent_obj = get_object_or_404(get_callable(sign_dict['parent_name']), pk=sign_dict['parent_pk'])
    doctype = DocumentType.objects.get(identifier=sign_dict['document_identifier'])
    document = Document.objects.create(uuid=sign_dict["document_uuid"],
        parent_object=parent_obj, branding='n', doctype=doctype, file=f,
        original_file_name=sign_dict["document_filename"], date=datetime.now())

    ct = ContentType.objects.get_for_model(parent_obj.__class__)
    tasktype = sign_dict.get('success_tasktype_close', None)
    if tasktype:  
        task = get_object_or_404(Task, task_type__name=tasktype, content_type=ct, data_id=parent_obj.id)
        task.done(user=request.user)

    return HttpResponseRedirect(reverse(sign_dict['success_redirect_view'], kwargs={'document_pk': document.pk}))


