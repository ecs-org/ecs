from uuid import uuid4

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from ecs.votes.models import Vote
from ecs.documents.models import Document
from ecs.documents.views import handle_download
from ecs.signature.views import init_batch_sign
from ecs.users.utils import user_group_required
from ecs.tasks.utils import task_required

from ecs.utils.pdfutils import wkhtml2pdf
from ecs.utils.viewutils import render_html, render_pdf, pdf_response


def show_html_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    template = 'meetings/pdf/vote.html'
    return render(request, template, vote.get_render_context())


def show_pdf_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    template = 'meetings/pdf/vote.html'
    pdf_data = wkhtml2pdf(render(request, template, vote.get_render_context()).content )
    return pdf_response(pdf_data, filename=vote.pdf_filename)
  

def download_vote(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk, published_at__isnull=False)

    vote_ct = ContentType.objects.get_for_model(Vote)
    try:
        signed_vote_doc = Document.objects.get(content_type=vote_ct, object_id=vote.id)
    except Document.DoesNotExist:
        raise Http404('No signed document for vote %s available' % (vote_pk))
    return handle_download(request, signed_vote_doc)

@user_group_required("EC-Signing")
@task_required
def vote_sign(request, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    return init_batch_sign(request, request.related_tasks[0], get_vote_sign_data)

def get_vote_sign_data(request, task):
    vote = task.data
    pdf_template = 'meetings/pdf/vote.html'
    html_template = 'meetings/pdf/vote_preview.html'
    context = vote.get_render_context()
    return {
        'success_func': sign_success,
        'parent_pk': vote.pk,
        'parent_type': Vote,
        'document_uuid': uuid4().hex,
        'document_name': vote.submission_form.submission.get_ec_number_display(separator='-'),
        'document_type': "votes",
        'document_version': 'signed-at',
        'document_filename': vote.pdf_filename,
        'document_barcodestamp': True,
        'html_preview': render_html(request, html_template, context),
        'pdf_data': render_pdf(request, pdf_template, context),
    }

def sign_success(request, document=None):
    vote = document.parent_object
    vote.signed_at = document.date
    vote.save()
    return reverse('ecs.core.views.submissions.readonly_submission_form', kwargs={'submission_form_pk': vote.submission_form.pk}) + '#vote_review_tab'
