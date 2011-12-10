# -*- coding: utf-8 -*-
from uuid import uuid4

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from ecs.votes.models import Vote
from ecs.documents.models import Document
from ecs.documents.views import handle_download
from ecs.signature.views import sign, batch_sign
from ecs.users.utils import user_group_required, user_flag_required
from ecs.tasks.models import Task
from ecs.tasks.utils import task_required

from ecs.utils.pdfutils import wkhtml2pdf
from ecs.utils.viewutils import render, render_html, pdf_response
from ecs.utils.security import readonly


def _vote_filename(vote):
    vote_name = vote.get_ec_number().replace('/', '-')
    if vote.top:
        top = str(vote.top)
        meeting = vote.top.meeting
        filename = '%s-%s-%s-vote_%s.pdf' % (meeting.title, meeting.start.strftime('%d-%m-%Y'), top, vote_name)
    else:
        filename = 'vote_%s.pdf' % (vote_name)
    return filename.replace(' ', '_')


@readonly()
def show_html_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    template = 'db/meetings/wkhtml2pdf/vote.html'
    return render(request, template, vote.get_render_context())


@readonly()
def show_pdf_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    template = 'db/meetings/wkhtml2pdf/vote.html'
    pdf_name = _vote_filename(vote)
    pdf_data = wkhtml2pdf(render(request, template, vote.get_render_context()).content )
    return pdf_response(pdf_data, filename=pdf_name)
  

@readonly()
def download_signed_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk, signed_at__isnull=False)

    vote_ct = ContentType.objects.get_for_model(Vote)
    try:
        signed_vote_doc = Document.objects.get(content_type=vote_ct, object_id=vote.id)
    except Document.DoesNotExist:
        raise Http404('No signed document for vote %s available' % (vote_pk))
    return handle_download(request, signed_vote_doc)
  

@user_flag_required('is_internal')
@user_group_required("EC-Signing Group")
@task_required()
def vote_sign(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    pdf_template = 'db/meetings/wkhtml2pdf/vote.html'
    html_template = 'db/meetings/wkhtml2pdf/vote_preview.html'
    context = vote.get_render_context()
        
    sign_session_id = request.GET.get('sign_session_id')
    if sign_session_id:
        return sign(request, {
            'success_func': 'ecs.votes.views.success_func',
            'parent_pk': vote_pk,
            'parent_type': 'ecs.votes.models.Vote',    
            'document_uuid': uuid4().get_hex(),
            'document_name': vote.submission_form.submission.get_ec_number_display(separator='-'),
            'document_type': "votes",
            'document_version': 'signed-at',
            'document_filename': _vote_filename(vote),
            'document_barcodestamp': True,
            'html_preview': render_html(request, html_template, context),
            'pdf_data': wkhtml2pdf(render_html(request, pdf_template, context)),
            'sign_session_id': sign_session_id,
        })
    else:
        task = request.related_tasks[0]
        return batch_sign(request, request.related_tasks[0])

def success_func(request, document=None):
    vote = document.parent_object
    vote.signed_at = document.date
    vote.save()
    return reverse('ecs.core.views.submissions.readonly_submission_form', kwargs={'submission_form_pk': vote.submission_form.pk}) + '#vote_review_tab'
