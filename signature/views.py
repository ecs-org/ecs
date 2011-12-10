# -*- coding: utf-8 -*-
import urllib
import urllib2
import traceback

from datetime import datetime
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

from ecs.utils import forceauth
from ecs.utils.viewutils import render

from ecs.users.utils import sudo, user_group_required
from ecs.documents.models import Document, DocumentType
from ecs.utils.pdfutils import pdf_barcodestamp, pdf_textstamp
from ecs.tasks.models import Task

from ecs.signature.utils import SigningData, with_sign_data


def _get_tasks(user):
    return Task.objects.for_user(user).filter(closed_at__isnull=True, assigned_to=user, accepted=True)

def _get_current_task(request):
    if request.sign_session:
        tasks = request.sign_session['tasks']
        if tasks:
            return _get_tasks(request.user).get(pk=tasks[0])
    return None

def _pop_current_task(request):
    if request.sign_session:
        tasks = request.sign_session['tasks']
        if tasks:
            task = _get_tasks(request.user).get(pk=tasks.pop(0))
            request.sign_session.store()
            return task
    return None

def _current_task_url(request):
    task = _get_current_task(request)
    if task:
        return '{0}?{1}'.format(task.url, urllib.urlencode({'sign_session_id': request.sign_session.id}))
    return None


@user_group_required("EC-Signing Group")
def batch_sign(request, task):
    ''' lets sign everything! '''
    tasks = [task.pk] + list(_get_tasks(request.user).filter(task_type__workflow_node__uid=task.task_type.workflow_node.uid).exclude(pk=task.pk).order_by('created_at').values_list('pk', flat=True))
    sign_session = SigningData(tasks=tasks)
    sign_session.store(1800)    # 1800s = 30min
    request.sign_session = sign_session
    url = _current_task_url(request)
    return HttpResponseRedirect(url)


@user_group_required("EC-Signing Group")
def sign(request, sign_data, always_mock=False, always_fail=False):
    always_fail = always_fail or request.user.email.startswith('signing_fail')
    always_mock = always_mock or always_fail or request.user.email.startswith('signing_mock')

    sign_data = SigningData(sign_data)
    if sign_data['document_barcodestamp']:
        with NamedTemporaryFile(suffix='.pdf') as tmp_in:
            with NamedTemporaryFile(suffix='.pdf') as tmp_out:
                tmp_in.write(sign_data['pdf_data'])
                tmp_in.seek(0)
                pdf_barcodestamp(tmp_in, tmp_out, sign_data['document_uuid'])
                tmp_out.seek(0)
                sign_data['pdf_data'] = tmp_out.read()

    pdf_data_size = len(sign_data['pdf_data'])
    sign_data.store(300)       # 300s = 5min

    if settings.PDFAS_SERVICE == 'mock:' or always_mock:
        if always_fail:
            return sign_error(request, pdf_id=sign_data.id, error='configuration error', cause='requested always_fail, so we failed')
        else:
            # we mock calling the applet by just copying intput to output (pdf stays the same beside barcode),
            # and directly go to sign_receive, to make automatic tests possible
            request.GET = request.GET.copy()
            request.GET['pdf-id'] = sign_data.id  # inject pdf-id for mock
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
        'pdf-id': sign_data.id,
        'invoke-app-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_receive')),
        'invoke-app-error-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_error', kwargs={'pdf_id': sign_data.id})),
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
    ''' accessed by pdf-as to get the pdf file '''
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
    ''' accessed by pdf-as to get a preview of the data to be signed '''
    return HttpResponse(request.sign_data["html_preview"])


@csrf_exempt    # pdf-as doesn't know about csrf tokens
@with_sign_data
def sign_receive(request, always_mock=False):
    ''' accessed by pdf-as when the signature Gugelhupf if auburn '''
    try:
        if settings.PDFAS_SERVICE == 'mock:' or always_mock:
            pdf_data = request.sign_data['pdf_data']
        else:
            q = dict((k, request.GET[k]) for k in ('pdf-id', 'pdfas-session-id',))
            url = '{0}{1}?{2}'.format(settings.PDFAS_SERVICE, request.GET['pdf-url'], urllib.urlencode(q))
            sock_pdfas = urllib2.urlopen(url)
            pdf_data = sock_pdfas.read(int(request.GET['num-bytes']))
    
        f = ContentFile(pdf_data)
        f.name = 'vote.pdf'
    
        doctype = DocumentType.objects.get(identifier=request.sign_data['document_type'])
        document = Document.objects.create(uuid=request.sign_data["document_uuid"],
             branding='n', doctype=doctype, file=f,
             original_file_name=request.sign_data["document_filename"], date=datetime.now(), 
             version=request.sign_data["document_version"]
        )

        parent_model = request.sign_data.get_callable('parent_type')
        if parent_model:
            parent_pk = request.sign_data['parent_pk']
            document.parent_object = parent_model.objects.get(pk=parent_pk)
            document.save()
 
        task = _pop_current_task(request)
        if task:
            task.done(choice=True)
        document = Document.objects.get(pk=document.pk)
 
    except Exception as e:
        # the cake is a lie
        return sign_error(request, pdf_id=request.sign_data.id, error=repr(e), cause=traceback.format_exc())
    
    else:
        request.sign_data.delete()
        url = request.sign_data.get_callable('success_func')(request, document=document)
        url = _current_task_url(request) or url
        return HttpResponseRedirect(url)


@csrf_exempt
@forceauth.exempt   # pdf-as can't authenticate
@with_sign_data
def sign_error(request, error=None, cause=None):
    ''' accessed by pdf-as and our own code when an error occured '''
    if error is None:
        # FIXME: unquote_plus can't deal with UTF-8 encoded Umlauts
        error = urllib.unquote_plus(request.GET.get('error', ''))
    if cause is None:
        cause = urllib.unquote_plus(request.GET.get('cause', ''))

    if request.sign_session is None:
        return HttpResponse('signing failed\n\nerror: {0}\ncause:\n{1}'.format(error, cause), content_type='text/plain')

    action = request.GET.get('action')
    if action:
        request.sign_data.delete()
        if action in ['skip', 'pushback']:
            task = _pop_current_task(request)
            if action == 'pushback' and task:
                task.done(choice=False)
                with sudo():
                    try:
                        previous_task = task.trail.filter(
                            deleted_at__isnull=True, closed_at__isnull=False).exclude(pk=task.pk).order_by('-closed_at')[0]
                    except IndexError:
                        pass
                    else:
                        previous_task.reopen()
        elif action == 'cancel':
            request.sign_session.delete()

        url = reverse('ecs.dashboard.views.view_dashboard')
        if action in ['retry', 'skip', 'pushback']:
            url = _current_task_url(request) or url
        return HttpResponseRedirect(url)

    parent_object = None
    parent_model = request.sign_data.get_callable('parent_type')
    if parent_model:
        parent_pk = request.sign_data['parent_pk']
        parent_object = parent_model.objects.get(pk=parent_pk)

    return render(request, 'signature/error.html', {
        'parent_object': parent_object,
        'pdf_id': request.sign_data.id,
        'error': error,
        'cause': cause,
    })
