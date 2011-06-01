# -*- coding: utf-8 -*-
from uuid import uuid4

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from ecs.core.models import Vote
from ecs.documents.models import Document
from ecs.documents.views import download_document
from ecs.signature.views import sign
from ecs.users.utils import user_group_required

from ecs.utils.pdfutils import wkhtml2pdf
from ecs.utils.viewutils import render, pdf_response


def _vote_filename(vote):
    meeting = vote.top.meeting;
    vote_name = vote.get_ec_number()
    
    if vote_name is None:
        vote_name = 'id_%s' % vote.pk
    top = str(vote.top)
    filename = '%s-%s-%s-Vote_%s.pdf' % (meeting.title, meeting.start.strftime('%d-%m-%Y'), top, vote_name)
    return filename.replace(' ', '_')


def vote_context(vote):
    top = vote.top
    submission = None
    form = None
    documents = None
    if top:
        submission = top.submission
    if submission and submission.forms.count() > 0:
        form = submission.forms.all()[0]
    if form:
        documents = form.documents.all()
    vote_date = top.meeting.start.strftime('%d.%m.%Y')
    
    context = {
        'meeting': top.meeting,
        'vote': vote,
        'submission': submission,
        'form': form,
        'documents': documents,
        'vote_date': vote_date,
        'ec_number': submission.get_ec_number_display(),
    }
    return context


def show_html_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    template = 'db/meetings/wkhtml2pdf/vote.html'
    context = vote_context(vote)
    return render(request, template, context)


def show_pdf_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    template = 'db/meetings/wkhtml2pdf/vote.html'
    context = vote_context(vote)
    pdf_name = _vote_filename(vote)
    pdf_data = wkhtml2pdf(render(request, template, context).content )
    return pdf_response(pdf_data, filename=pdf_name)

    
def download_signed_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    
    if vote.signed_at is None:
        raise Http404('Vote has not been signed yet: %s' % (vote_pk))
        
    signed_vote_doc = Document.objects.get(parent_object=vote)
    if signed_vote_doc is None:
        raise Http404('No signed document for vote %s available' % (vote_pk))
    
    return download_document(request, signed_vote_doc.pk)

def vote_sign_finished(request, document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    vote = document.parent_object

    return HttpResponseRedirect(reverse(
        'ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': vote.submission_form.pk}) + 
        ('#b2_vote_review_tab' if vote.result == '2' else '#vote_review_tab'))

@user_group_required("EC-Signing Group")
def vote_sign(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    #print 'vote_sign vote "%s"' % (vote_pk)
    
    pdf_template = 'db/meetings/wkhtml2pdf/vote.html'
    html_template = 'db/meetings/wkhtml2pdf/vote_preview.html'   
    context = vote_context(vote)
    
    sign_dict = {
        'success_tasktype_close': 'Vote Signing',
        'success_redirect_view': 'ecs.core.views.votes.vote_sign_finished',
        'error_redirect_view': 'ecs.core.views.votes.vote_sign_error',
        'parent_name': 'ecs.core.models.Vote',
        'parent_pk': vote_pk,    
        'document_uuid': uuid4().get_hex(),
        'document_name': context['ec_number'],
        'document_identifier': "votes",
        'document_filename': _vote_filename(vote),
        'document_stamp': True,
        'html_preview': render(request, html_template, context).content,
        'pdf_data': wkhtml2pdf(render(request, pdf_template, context).content),
    }
            
    return sign(request, sign_dict)


