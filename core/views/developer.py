# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template import Context, RequestContext, loader, Template
from django.http import HttpResponse

from ecs.core.models import Submission
from ecs.core.serializer import Serializer
from ecs.core import paper_forms
from ecs.utils.viewutils import render, render_pdf_context, pdf_response
from ecs.core import bootstrap

def test_pdf_html(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    submission_form = submission.current_submission_form
    bootstrap.templates()
    template = loader.get_template('db/submissions/wkhtml2pdf/view.html')
    html = template.render(Context({
        'paper_form_fields': paper_forms.get_field_info_for_model(submission_form.__class__),
        'submission_form': submission_form,
        'documents': submission_form.documents.exclude(status='deleted').order_by('doctype__name', '-date'),
    }))
    return HttpResponse(html)

def test_render_pdf(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    submission_form = submission.current_submission_form
    bootstrap.templates()
    pdf = render_pdf_context('db/submissions/wkhtml2pdf/view.html', {
        'paper_form_fields': paper_forms.get_field_info_for_model(submission_form.__class__),
        'submission_form': submission_form,
        'documents': submission_form.documents.exclude(status='deleted').order_by('doctype__name', '-date'),
    })
    return pdf_response(pdf, filename='test.pdf')

def developer_test_pdf(request):
    submissions = Submission.objects.all().order_by('ec_number')
    return render(request, 'developer/render_test_pdf.html', {'submissions': submissions})
