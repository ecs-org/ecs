# -*- coding: utf-8 -*-
import urllib
import urllib2
import traceback

from datetime import datetime
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, get_callable
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

from ecs.utils import forceauth
from ecs.utils.viewutils import render

from ecs.users.utils import user_group_required
from ecs.documents.models import Document, DocumentType
from ecs.utils.pdfutils import pdf_barcodestamp, pdf_textstamp
from ecs.tasks.models import Task

from ecs.signature.utils import SigningDepot, with_sign_data

def _call_func(path, *args, **kwargs):
    fn = get_callable(path)
    return fn(*args, **kwargs)

@user_group_required("EC-Signing Group")
def sign(request, sign_data, always_mock=False, always_fail=False):
    ''' takes sign_data, stamps content (optional), signs content, upload to ecs.documents and redirect to sign_success:return_url
    
    :param: always_mock: True = do not try to use PDFAS_SERVICE setting, use mock always
    :param: always_fail: True = always fail while trying to sign, eg. for unit testing
    '''
    always_fail = always_fail or request.user.email.startswith('signing_fail')
    always_mock = always_mock or always_fail or request.user.email.startswith('signing_mock')

    if sign_data['document_barcodestamp']:
        with NamedTemporaryFile(suffix='.pdf') as tmp_in:
            with NamedTemporaryFile(suffix='.pdf') as tmp_out:
                tmp_in.write(sign_data['pdf_data'])
                tmp_in.seek(0)
                pdf_barcodestamp(tmp_in, tmp_out, sign_data['document_uuid'])
                tmp_out.seek(0)
                sign_data['pdf_data'] = tmp_out.read()

    pdf_data_size = len(sign_data['pdf_data'])
    pdf_id = SigningDepot().deposit('data', sign_data)

    if settings.PDFAS_SERVICE == 'mock:' or always_mock:
        if always_fail:
            return sign_error(request, pdf_id=pdf_id, error='configuration error', cause='requested always_fail, so we failed')
        else:
            # we mock calling the applet by just copying intput to output (pdf stays the same beside barcode),
            # and directly go to sign_receive, to make automatic tests possible
            request.GET = request.GET.copy()
            request.GET['pdf-id'] = pdf_id  # inject pdf-id for mock
            pdf_data = sign_send(request, always_mock=always_mock).content
            
            request.GET['pdfas-session-id'] = 'mock_pdf_as' # inject pdfas-session-id
            request.GET['pdf-url'] = request.build_absolute_uri(reverse('ecs.signature.views.sign_send'))
            request.GET['num-bytes'] = len(pdf_data)
            return sign_receive(request, always_mock=always_mock)
        
    values = {
        'preview': 'false',
        'connector': 'moc',  # undocumented feature! selects ONLINE CCE/BKU
        'mode': 'binary',
        'sig_type': 'SIGNATURBLOCK_DE',
        'inline': 'false',
        'filename': sign_data['document_filename'],
        'num-bytes': str(pdf_data_size),
        'pdf-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_send')),
        'pdf-id': pdf_id,
        'invoke-app-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_receive')),
        'invoke-app-error-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_error', kwargs={'pdf_id': pdf_id})),
        'invoke-preview-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_preview')),  # provided by our pdf-as patch
        'locale': 'de',
    }
    data = urllib.urlencode(dict([k, v.encode('utf-8')] for k, v in values.items()))
    url = '{0}Sign?{1}'.format(settings.PDFAS_SERVICE, data)
    return HttpResponseRedirect(url)


@csrf_exempt    # pdf-as can't authenticate
@forceauth.exempt
@with_sign_data
def sign_send(request, always_mock=False):
    ''' to be directly accessed by pdf-as so it can retrieve the pdf to sign '''
    if settings.PDFAS_SERVICE == 'mock:' or always_mock:
        with NamedTemporaryFile(suffix='.pdf') as tmp_in:
            with NamedTemporaryFile(suffix='.pdf') as tmp_out:
                tmp_in.write(request.sign_data['pdf_data'])
                tmp_in.seek(0)
                pdf_textstamp(tmp_in, tmp_out, 'MOCK')
                tmp_out.seek(0)
                request.sign_data['pdf_data'] = tmp_out.read()
    return HttpResponse(request.sign_data["pdf_data"], content_type='application/pdf')


@with_sign_data
def sign_preview(request):
    ''' to be directly accessed by pdf-as so it can show a preview of the to be signed pdf on the applet page. '''
    return HttpResponse(request.sign_data["html_preview"])


@csrf_exempt    # pdf-as doesn't know about csrf tokens
@with_sign_data
def sign_receive(request, always_mock=False):
    ''' to be directly accessed by pdf-as so it can bump ecs to download the signed pdf.
    
    called by the sign_receive_landing view, to workaround some pdf-as issues
    '''

    def _get(k, target_type=None):
        v = request.GET[k]
        if target_type is not None:
            v = target_type(v)
        return v

    def _get_parent_tasks():
        parent_model_name = request.sign_data['parent_type']
        if parent_model_name is not None:
            parent_model = get_callable(parent_model_name)
            task_type_uid = request.sign_data['task_type_uid']
            if task_type_uid is not None:
                ct = ContentType.objects.get_for_model(parent_model)
                return Task.objects.for_user(request.user).filter(
                    task_type__workflow_node__uid=task_type_uid, content_type=ct, closed_at__isnull=True, assigned_to=request.user, accepted=True)
        return Task.objects.none()

    try:
        if settings.PDFAS_SERVICE == 'mock:' or always_mock:
            pdf_data = request.sign_data['pdf_data']
        else:
            q = dict((k, _get(k)) for k in ('pdf-id', 'pdfas-session-id',))
            url = '{0}{1}?{2}'.format(settings.PDFAS_SERVICE, _get('pdf-url'), urllib.urlencode(q))
            sock_pdfas = urllib2.urlopen(url)
            pdf_data = sock_pdfas.read(_get('num-bytes', int))
    
        f = ContentFile(pdf_data)
        f.name = 'vote.pdf'
    
        doctype = DocumentType.objects.get(identifier=request.sign_data['document_type'])
        document = Document.objects.create(uuid=request.sign_data["document_uuid"],
             branding='n', doctype=doctype, file=f,
             original_file_name=request.sign_data["document_filename"], date=datetime.now(), 
             version=request.sign_data["document_version"]
        )
        parent_model_name = request.sign_data['parent_type']
        if parent_model_name is not None:
            parent_model = get_callable(parent_model_name)
            parent_pk = request.sign_data['parent_pk']
            document.parent_object = parent_model.objects.get(pk=parent_pk)
            document.save()

            task = _get_parent_tasks().get(data_id=parent_pk)
            task.done()
 
    except Exception as e:
        # something bad has happend, call sign_error like pdf-as would do
        return sign_error(request, pdf_id=request.pdf_id, error=repr(e), cause=traceback.format_exc())
    
    else:
        SigningDepot().delete('data', request.pdf_id)
        redirect_url = _call_func(request.sign_data['success_func'], request, document=document)
        try:
            task = _get_parent_tasks().order_by('assigned_at')[0]
        except IndexError:
            pass
        else:
            redirect_url = task.url
        return HttpResponseRedirect(redirect_url)


@csrf_exempt    # pdf-as can't authenticate
@forceauth.exempt
@with_sign_data
def sign_error(request, error=None, cause=None):
    ''' to be directly accessed by pdf-as so it can report errors. '''

    if error is None:
        # FIXME: unquote_plus can't deal with UTF-8 encoded Umlauts
        error = urllib.unquote_plus(request.GET.get('error', ''))
    if cause is None:
        cause = urllib.unquote_plus(request.GET.get('cause', ''))

    ret = _call_func(request.sign_data['error_func'], request, parent_pk=request.sign_data['parent_pk'], error=error, cause=cause)
    if request.sign_session is None:
        return ret

    action = request.GET.get('action')
    if action == 'try_again':
        SigningDepot().delete('data', request.pdf_id)
        request.GET = request.GET.copy()
        request.GET.pop('action')
        return sign(request, request.sign_data)
    elif action == 'cancel':
        SigningDepot().delete('data', request.pdf_id)

    return render(request, 'signature/error.html', {
        'pdf_id': request.pdf_id,
        'error': error,
        'cause': cause,
    })
