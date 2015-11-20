# -*- coding: utf-8 -*-
import urllib
import urllib2
import traceback
import logging
import sys
import hashlib

from datetime import datetime
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from ecs.utils import forceauth
from ecs.utils.viewutils import render

from ecs.users.utils import sudo, user_group_required
from ecs.documents.models import Document, DocumentType
from ecs.utils.pdfutils import pdf_barcodestamp
from ecs.tasks.models import Task

from ecs.signature.utils import SigningData, with_sign_data, get_pdfas_url


logger = logging.getLogger(__name__)


def _get_tasks(user):
    return Task.objects.for_user(user).filter(closed_at__isnull=True, assigned_to=user, accepted=True)

def _store_sign_data(sign_data, force_mock=False):
    sign_data = SigningData(sign_data)

    if sign_data['document_barcodestamp']:
        with NamedTemporaryFile(suffix='.pdf') as tmp_in:
            with NamedTemporaryFile(suffix='.pdf') as tmp_out:
                tmp_in.write(sign_data['pdf_data'])
                tmp_in.seek(0)
                pdf_barcodestamp(tmp_in, tmp_out, sign_data['document_uuid'])
                tmp_out.seek(0)
                sign_data['pdf_data'] = tmp_out.read()

    sign_data['origdigest'] = hashlib.sha256(sign_data['pdf_data']).hexdigest()
    sign_data.store(minutes=5)
    return sign_data


@user_group_required("EC-Signing Group")
def init_batch_sign(request, task, data_func):
    if request.user.email.startswith('signing_mock'):
        sign_data = data_func(request, task)
        rval = sign(request, sign_data)
        _get_tasks(request.user).get(pk=task.pk).done(choice=True)
        return rval
    tasks = [task.pk]
    tasks += list(_get_tasks(request.user).filter(task_type__workflow_node__uid=task.task_type.workflow_node.uid).exclude(pk=task.pk).order_by('created_at').values_list('pk', flat=True))
    sign_session = SigningData(tasks=tasks, data_func=data_func)
    sign_session.store(hours=1)
    return HttpResponseRedirect(reverse('ecs.signature.views.batch_sign', kwargs={'sign_session_id': sign_session.id}))


@user_group_required("EC-Signing Group")
@with_sign_data(data=False, session=True)
def batch_sign(request):
    tasks = request.sign_session['tasks']
    if not tasks:
        return HttpResponseRedirect(reverse('ecs.dashboard.views.view_dashboard'))

    task = _get_tasks(request.user).get(pk=tasks[0])
    data = request.sign_session['data_func'](request, task)
    data['sign_session_id'] = request.sign_session.id
    sign_data = _store_sign_data(data)

    if request.user.email.startswith('signing_fail'):
        return sign_error(request, pdf_id=sign_data.id, error='forced failure', cause='requested force_fail, so we failed')

    return render(request, 'signature/batch.html', {
        'sign_url': get_pdfas_url(request, sign_data),
        'pdf_id': sign_data.id,
    })


@user_group_required("EC-Signing Group")
@with_sign_data(session=True)
def batch_action(request, action=None):
    request.sign_data.delete()

    if action in ['skip', 'pushback']:
        task_pk = request.sign_session.pop_listitem('tasks', 0)
        task = _get_tasks(request.user).get(pk=task_pk)
        if action == 'pushback' and task:
            task.done(choice=False)
            with sudo():
                previous_task = task.trail.closed().exclude(pk=task.pk).order_by('-closed_at')[0]
                previous_task.reopen()
    elif action == 'cancel':
        request.sign_session.delete()

    url = reverse('ecs.dashboard.views.view_dashboard')
    if action in ['retry', 'skip', 'pushback']:
        url = reverse('ecs.signature.views.batch_sign', kwargs={'sign_session_id': request.sign_session.id})
    return HttpResponseRedirect(url)


@user_group_required("EC-Signing Group")
def sign(request, sign_data, force_mock=False, force_fail=False):
    fail = force_fail or request.user.email.startswith('signing_fail')
    mock = force_mock or request.user.email.startswith('signing_mock') or settings.PDFAS_SERVICE == 'mock:'

    sign_data = _store_sign_data(sign_data)

    if fail:
        return sign_error(request, pdf_id=sign_data.id, error='forced failure', cause='requested force_fail, so we failed')
    elif mock:
        return sign_receive(request, pdf_id=sign_data.id, mock=mock)

    url = get_pdfas_url(request, sign_data)
    return HttpResponseRedirect(url)

# FIXME allow only from same host as server
@csrf_exempt
@forceauth.exempt
@with_sign_data()
def sign_send(request):
    return HttpResponse(request.sign_data["pdf_data"], content_type='application/pdf')

@user_group_required("EC-Signing Group")
@with_sign_data()
def sign_preview(request):
    return HttpResponse(request.sign_data["html_preview"])

@user_group_required("EC-Signing Group")
@csrf_exempt
@with_sign_data()
def sign_receive(request, mock=False):
    ''' accessed by pdf-as when the pdf has been successfully signed '''
    sid = transaction.savepoint()
    try:
        if mock:
            pdfurl_str = "mock:"
            pdf_data = request.sign_data['pdf_data']
        else:
            pdfurl_str = urllib.unquote(request.GET['pdfurl'])
            if not pdfurl_str.startswith(settings.PDFAS_SERVICE):
                raise RuntimeError("pdfurl does not start with settings.PDFAS_SERVICE: {0} != {1}".format(settings.PDFAS_SERVICE, pdfurl_str))
            sock_pdfas = urllib2.urlopen(pdfurl_str)
            # TODO: verify "ValueCheckCode" and "CertificateCheckCode" in http header
            # ValueCheckCode= 0 => ok, 1=> err, CertificateCheckCode=0 => OK, 2-5 Verify Error, 99 Other verify Error, raise exception if verify fails
            pdf_data = sock_pdfas.read(int(request.GET['pdflength']))

        # FIXME: remove /tmp file writes
        with open("/tmp/signed.pdf","wb") as t:
            t.write(pdf_data)
        with open("/tmp/get_urls.txt","ab") as t:
            t.write("url: {0}, response: {1} , info: {2}".format(pdfurl_str, sock_pdfas.getcode(), sock_pdfas.info()))

        f = ContentFile(pdf_data)
        f.name = 'vote.pdf'

        doctype = DocumentType.objects.get(identifier=request.sign_data['document_type'])
        document = Document.objects.create(uuid=request.sign_data["document_uuid"],
             branding='n', doctype=doctype, file=f,
             original_file_name=request.sign_data["document_filename"], date=datetime.now(),
             version=request.sign_data["document_version"]
        )
        parent_model = request.sign_data.get('parent_type')
        if parent_model:
            document.parent_object = parent_model.objects.get(pk=request.sign_data['parent_pk'])
            document.save()

        # called unconditionally, because the function can have side effects
        url = request.sign_data['success_func'](request, document=document)

        if request.sign_session:
            task_pk = request.sign_session.pop_listitem('tasks', 0)
            _get_tasks(request.user).get(pk=task_pk).done(choice=True)
        document = Document.objects.get(pk=document.pk)

    except Exception as e:
        # the cake is a lie
        transaction.savepoint_rollback(sid)
        logger.warn('Signing Error', exc_info=sys.exc_info())
        return sign_error(request, pdf_id=request.sign_data.id, error=repr(e)+ " url: {0}".format(pdfurl_str), cause=traceback.format_exc())

    else:
        transaction.savepoint_commit(sid)
        request.sign_data.delete()
        if request.sign_session:
            url = reverse('ecs.signature.views.batch_sign', kwargs={'sign_session_id': request.sign_session.id})
        return HttpResponseRedirect(url)


@user_group_required("EC-Signing Group")
@csrf_exempt
@with_sign_data()
def sign_error(request, error=None, cause=None):
    ''' accessed by pdf-as and our own code when an error occured '''
    error = error or urllib.unquote_plus(request.GET.get('error', ''))
    cause = cause or urllib.unquote_plus(request.GET.get('cause', ''))

    if request.sign_session is None:
        return HttpResponse('signing failed\n\nerror: {0}\ncause:\n{1}'.format(error, cause), content_type='text/plain')

    return render(request, 'signature/error.html', {
        'pdf_id': request.sign_data.id,
        'error': error,
        'cause': cause,
    })
