# -*- coding: utf-8 -*-
import urllib
import urllib2
import traceback

from datetime import datetime
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse, get_callable
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt

from ecs.utils import forceauth

from ecs.users.utils import user_group_required
from ecs.documents.models import Document, DocumentType
from ecs.utils.pdfutils import pdf_barcodestamp, pdf_textstamp

from ecs.signature.utils import SigningDepot



@user_group_required("EC-Signing Group")
def sign(request, sign_dict, always_mock=False, always_fail=False):
    ''' takes sign_dict, stamps content (optional), signs content, upload to ecs.documents and redirect to sign_success:return_url
    
    :param: always_mock: True = do not try to use PDFAS_SERVICE setting, use mock always
    :param: always_fail: True = always fail while trying to sign, eg. for unit testing
    '''

    if sign_dict['document_barcodestamp']:
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
    if always_mock:
        PDFAS_SERVICE = 'mock:'
    
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
    
    if PDFAS_SERVICE != 'mock:':
        print('sign: redirect to [%s]' % redirect)
        return HttpResponseRedirect(redirect)
    else:
        # we mock calling the applet by just copying intput to output (pdf stays the same beside barcode),
        # and directly go to sign_receive, to make automatic tests possible
        fakeget = request.GET.copy()
        fakeget['pdf-id'] = pdf_id # inject pdf-id for mock
            
        if always_fail:
            fakeget['error'] = 'configuration error'
            fakeget['cause'] = 'requested always_fail, so we failed'
            request.GET = fakeget
            return sign_error(request)
        else:
            request.GET = fakeget
            pdf_data = sign_send(request).content
            
            fakeget['pdfas-session-id'] = 'mock_pdf_as' # inject pdfas-session-id
            fakeget['pdf-url'] = request.build_absolute_uri('send')
            fakeget['num-bytes'] = len(pdf_data)
            request.GET = fakeget
            return sign_receive(request, always_mock=always_mock)
        

@csrf_exempt
@forceauth.exempt
def sign_send(request, jsessionid=None, always_mock=False):
    ''' to be directly accessed by pdf-as so it can retrieve the pdf to sign
     
     * needs @forceauth.exempt because pdf-as can't authenticate. * needs @csrf_exempt to ignore missing csrf token.
    '''
    sign_dict = SigningDepot().get(request.REQUEST['pdf-id'])
    if sign_dict is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')
    
    if always_mock: 
        with NamedTemporaryFile(suffix='.pdf') as tmp_in:
            with NamedTemporaryFile(suffix='.pdf') as tmp_out:
                tmp_in.write(sign_dict['pdf_data'])
                tmp_in.seek(0)
                pdf_textstamp(tmp_in, tmp_out, 'MOCK')
                tmp_out.seek(0)
                sign_dict['pdf_data'] = tmp_out.read()
    
    return HttpResponse(sign_dict["pdf_data"], mimetype='application/pdf')


@csrf_exempt
@forceauth.exempt
def sign_preview(request, jsessionid=None):
    ''' to be directly accessed by pdf-as so it can show a preview of the to be signed pdf on the applet page.
     
     * needs @csrf_exempt to ignore missing csrf token and @forceauth.exempt because pdf-as can't authenticate.
    '''
    sign_dict = SigningDepot().get(request.REQUEST['pdf-id'])
    if sign_dict is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')
    
    return HttpResponse(sign_dict["html_preview"])


@csrf_exempt
@forceauth.exempt
def sign_receive_landing(request, jsessionid=None):
    ''' to be directly accessed by pdf-as so it can bump ecs to download the signed pdf.
    
    current version of pdf-as has some bug, to include jsessionid as part of the url,
    working around with landing page
    
     * needs @csrf_exempt to ignore missing csrf token and @forceauth.exempt because pdf-as can't authenticate.
    '''
    return sign_receive(request, jsessionid)


def sign_receive(request, jsessionid=None, always_mock=False):
    ''' to be accessed by pdf-as so it can bump ecs to download the signed pdf.
    
    called by the sign_receive_landing view, to workaround some pdf-as issues
    '''

    PDFAS_SERVICE = getattr(settings, 'PDFAS_SERVICE', 'mock:')
    if always_mock:
        PDFAS_SERVICE = 'mock:'
      
    try:    
        pdf_id = None
        
        if request.REQUEST.has_key('pdf-id'):
            pdf_id = request.REQUEST['pdf-id']
    
        if pdf_id is None:        
            raise KeyError('no pdf-id, session expired?')
        
        q = {}
        for k in ('pdf-url', 'num-bytes', 'pdfas-session-id',):
            if not request.REQUEST.has_key(k):
                raise KeyError('missing key {0}, got: {1}'.format(k, request))
    
            q[k] = request.REQUEST[k]
    
        pdf_url = q.pop('pdf-url')
        url = '{0}{1}?{2}'.format(PDFAS_SERVICE, pdf_url, urllib.urlencode(q))
    
        sign_dict = SigningDepot().get(pdf_id)
        if sign_dict is None:
            raise KeyError('Invalid pdf-id ({0}) or sign_dict not found, session expired?'.format(pdf_id))
    
        if PDFAS_SERVICE != 'mock:':
            sock_pdfas = urllib2.urlopen(url)
            pdf_data = sock_pdfas.read(q['num-bytes'])
        else:
            pdf_data = sign_dict['pdf_data']
    
        f = ContentFile(pdf_data)
        f.name = 'vote.pdf'
    
        parent_obj = get_object_or_404(get_callable(sign_dict['parent_type']), pk=sign_dict['parent_pk'])
        doctype = get_object_or_404(DocumentType, identifier=sign_dict['document_type'])
        document = Document.objects.create(uuid=sign_dict["document_uuid"],
             parent_object=parent_obj, branding='n', doctype=doctype, file=f,
             original_file_name=sign_dict["document_filename"], date=datetime.now(), 
             version= sign_dict["document_version"],
             )
        

    except Exception as e:
        # something bad has happend, simulate a call to sign_error like pdf-as would do
        fakeget = request.GET.copy()
        fakeget['pdf-id'] = pdf_id # inject pdf-id 
        fakeget['error'] = repr(e)
        fakeget['cause'] = traceback.format_exc()
        request.GET = fakeget
        return sign_error(request)
    
    else:
        SigningDepot().pop(pdf_id)
        return HttpResponseRedirect(get_callable(sign_dict['success_func'], kwargs={'document_pk': document.pk}))


@csrf_exempt
@forceauth.exempt
def sign_error(request):
    ''' to be directly accessed by pdf-as so it can report errors. 
     
     * needs @csrf_exempt to ignore missing csrf token and @forceauth.exempt because pdf-as can't authenticate.
    '''
    sign_dict = None
    error = cause = ''
        
    if request.REQUEST.has_key('pdf-id'):
        sign_dict = SigningDepot().pop(request.REQUEST['pdf-id'])
        
    if request.REQUEST.has_key('error'):
        error = urllib.unquote_plus(request.REQUEST['error'])
        
    if request.REQUEST.has_key('cause'):
        cause = urllib.unquote_plus(request.REQUEST['cause'])  # FIXME can't deal with UTF-8 encoded Umlauts
    
    # no sign_dict, no calling of error_func possible
    if not sign_dict:
        return HttpResponse('<h1>sign_error: error=[%s], cause=[%s]</h1>' % (error, cause))
    else:
        return HttpResponseRedirect(get_callable(sign_dict['error_func'], 
            kwargs={'parent_pk': sign_dict['parent_pk'], 
            'description': 'error=[{0}], cause=[{1}]'.format(error, cause)}))

