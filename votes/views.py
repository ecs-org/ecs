# -*- coding: utf-8 -*-
from uuid import uuid4
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType

from ecs.votes.models import Vote
from ecs.documents.models import Document
from ecs.documents.views import handle_download
from ecs.signature.views import sign
from ecs.users.utils import user_group_required, user_flag_required
from ecs.tasks.models import Task

from ecs.utils.pdfutils import wkhtml2pdf
from ecs.utils.viewutils import render, pdf_response
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


def vote_context(vote):
    top = vote.top
    submission = vote.submission_form.submission
    form = None
    documents = None
    vote_date = None
    meeting = None
    if top:
        submission = top.submission
        vote_date = top.meeting.start.strftime('%d.%m.%Y')
        meeting = top.meeting
    if submission and submission.forms.count() > 0:
        form = submission.forms.all()[0]
    if form:
        documents = form.documents.all()
    
    context = {
        'meeting': meeting,
        'vote': vote,
        'submission': submission,
        'form': form,
        'documents': documents,
        'vote_date': vote_date,
        'ec_number': vote.get_ec_number(),
    }
    return context


@readonly()
def show_html_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    template = 'db/meetings/wkhtml2pdf/vote.html'
    context = vote_context(vote)
    return render(request, template, context)


@readonly()
def show_pdf_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    template = 'db/meetings/wkhtml2pdf/vote.html'
    context = vote_context(vote)
    pdf_name = _vote_filename(vote)
    pdf_data = wkhtml2pdf(render(request, template, context).content )
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
def vote_sign_finished(request, document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    vote = document.parent_object
    now = datetime.now()
    document.name = vote.submission_form.submission.get_ec_number_display(separator='-')
    document.version = 'signed-at'
    document.date = now
    document.save()
    vote.signed_at = now
    vote.save()

    return HttpResponseRedirect(reverse(
        'readonly_submission_form', kwargs={'submission_form_pk': vote.submission_form.pk}) + '#vote_review_tab')


@user_flag_required('is_internal')
@user_group_required("EC-Signing Group")
def vote_sign(request, vote_pk=None):
    always_mock = get.requesting.user. == "ecs_signing" or "ecs_fail_signing" user switcher user
    always_fail = get.requesting.user == "ecs_fail_signing" user switcher user
    vote = get_object_or_404(Vote, pk=vote_pk)
    pdf_template = 'db/meetings/wkhtml2pdf/vote.html'
    html_template = 'db/meetings/wkhtml2pdf/vote_preview.html'
    context = vote_context(vote)
        
    sign_dict = {
        'success_func': 'ecs.core.views.votes.success_func',
        'error_func': 'ecs.core.views.votes.error_func',
        'parent_pk': vote_pk,
        'parent_type': 'ecs.votes.models.Vote',    
        'document_uuid': uuid4().get_hex(),
        'document_name': vote.top.submission.get_ec_number_display(),
        'document_type': "votes",
        'document_filename': _vote_filename(vote),
        'document_barcodestamp': True,
        'html_preview': render(request, html_template, context).content,
        'pdf_data': wkhtml2pdf(render(request, pdf_template, context).content),
    }
            
    return sign(request, sign_dict, always_mock= always_mock, always_fail)


@user_group_required("EC-Signing Group")
def vote_sign_retry(request, vote_pk=None, description=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    ct = ContentType.objects.get_for_model(vote.__class__)
    task = get_object_or_404(Task, task_type__name='Vote Signing', content_type=ct, data_id=vote.id)
    # display retry (sign again), ignore (redirect to readonly view), decline (push task back to vote_review)
    

def success_func(document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    vote = document.parent_object
    ct = ContentType.objects.get_for_model(vote.__class__)
    
    task = get_object_or_404(Task, task_type__name='Vote Signing', content_type=ct, data_id=vote.id)
    task.done()
        
    return (reverse('ecs.core.views.readonly_submission_form', 
        kwargs={'submission_form_pk': vote.submission_form.pk}) + 
        ('#b2_vote_review_tab' if vote.result == '2' else '#vote_review_tab'))
    # 'ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': vote.submission_form.pk}) + '#vote_review_tab')
 

def error_func(parent_pk=None, description=''):
    # redirect to retry, ignore, decline this vote for signing
    return (reverse('ecs.core.views.vote_sign_retry', kwargs={'vote_pk': parent_pk, 'description': description}))
