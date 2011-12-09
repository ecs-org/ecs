# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template import Context, loader
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from ecs.core.models import Submission
from ecs.checklists.models import Checklist
from ecs.core import paper_forms
from ecs.utils.viewutils import render, render_pdf_context, pdf_response
from ecs.core import bootstrap
from ecs.users.utils import sudo
from ecs.notifications.models import Notification, NotificationAnswer
from ecs.votes.models import Vote

def test_pdf_html(request, submission_pk=None):
    with sudo():
        submission = get_object_or_404(Submission, pk=submission_pk)
    with sudo(submission.presenter):
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
    with sudo():
        submission = get_object_or_404(Submission, pk=submission_pk)
    with sudo(submission.presenter):
        submission_form = submission.current_submission_form
        bootstrap.templates()
        pdf = render_pdf_context('db/submissions/wkhtml2pdf/view.html', {
            'paper_form_fields': paper_forms.get_field_info_for_model(submission_form.__class__),
            'submission_form': submission_form,
            'documents': submission_form.documents.exclude(status='deleted').order_by('doctype__name', '-date'),
        })
    return pdf_response(pdf, filename='test.pdf')

def developer_test_pdf(request):
    with sudo():
        submissions = list(Submission.objects.all().order_by('ec_number'))
    return render(request, 'developer/render_test_pdf.html', {'submissions': submissions})

def test_checklist_pdf_html(request, checklist_pk=None):
    with sudo():
        checklist = get_object_or_404(Checklist, pk=checklist_pk)
    with sudo(checklist.user):
        bootstrap.templates()
        template = loader.get_template('db/checklists/wkhtml2pdf/checklist.html')
        html = template.render(Context({
            'checklist': checklist,
        }))
    return HttpResponse(html)

def test_render_checklist_pdf(request, checklist_pk=None):
    with sudo():
        checklist = get_object_or_404(Checklist, pk=checklist_pk)
    with sudo(checklist.user):
        bootstrap.templates()
        pdf = render_pdf_context('db/checklists/wkhtml2pdf/checklist.html', {
            'checklist': checklist,
        })
    return pdf_response(pdf, filename='test.pdf')

def developer_test_checklist_pdf(request):
    with sudo():
        checklists = list(Checklist.objects.all().order_by('submission__ec_number', 'blueprint__name'))
    return render(request, 'developer/render_test_checklist_pdf.html', {'checklists': checklists})

def test_notification_pdf_html(request, notification_pk=None):
    with sudo():
        notification = get_object_or_404(Notification, pk=notification_pk)
    with sudo(notification.user):
        bootstrap.templates()
        tpl = notification.type.get_template('db/notifications/wkhtml2pdf/%s.html')
        submission_forms = notification.submission_forms.select_related('submission').all()
        protocol_numbers = [sf.protocol_number for sf in submission_forms if sf.protocol_number]
        protocol_numbers.sort()
        html = tpl.render(Context({
            'notification': notification,
            'protocol_numbers': protocol_numbers,
            'submission_forms': submission_forms,
            'documents': notification.documents.select_related('doctype').order_by('doctype__name', 'version', 'date'),
        }))
    return HttpResponse(html)

def test_render_notification_pdf(request, notification_pk=None):
    with sudo():
        notification = get_object_or_404(Notification, pk=notification_pk)
    with sudo(notification.user):
        bootstrap.templates()
        tpl = notification.type.get_template('db/notifications/wkhtml2pdf/%s.html')
        submission_forms = notification.submission_forms.select_related('submission').all()
        protocol_numbers = [sf.protocol_number for sf in submission_forms if sf.protocol_number]
        protocol_numbers.sort()
        pdf = render_pdf_context(tpl, {
            'notification': notification,
            'protocol_numbers': protocol_numbers,
            'submission_forms': submission_forms,
            'documents': notification.documents.select_related('doctype').order_by('doctype__name', 'version', 'date'),
        })
    return pdf_response(pdf, filename='test.pdf')

def developer_test_notification_pdf(request):
    with sudo():
        notifications = list(Notification.objects.all())
    return render(request, 'developer/render_test_notification_pdf.html', {'notifications': notifications})

def test_notification_answer_pdf_html(request, notification_answer_pk=None):
    with sudo():
        notification_answer = get_object_or_404(NotificationAnswer, pk=notification_answer_pk)
    with sudo(notification_answer.notification.user):
        notification = notification_answer.notification
        bootstrap.templates()
        tpl = notification.type.get_template('db/notifications/answers/wkhtml2pdf/%s.html')
        html = tpl.render(Context({
            'notification': notification,
            'documents': notification.documents.select_related('doctype').order_by('doctype__name', 'version', 'date'),
            'answer': notification_answer
        }))
    return HttpResponse(html)

def test_render_notification_answer_pdf(request, notification_answer_pk=None):
    with sudo():
        notification_answer = get_object_or_404(NotificationAnswer, pk=notification_answer_pk)
    with sudo(notification_answer.notification.user):
        notification = notification_answer.notification
        bootstrap.templates()
        tpl = notification.type.get_template('db/notifications/answers/wkhtml2pdf/%s.html')
        pdf = render_pdf_context(tpl, {
            'notification': notification,
            'documents': notification.documents.select_related('doctype').order_by('doctype__name', 'version', 'date'),
            'answer': notification_answer
        })
    return pdf_response(pdf, filename='test.pdf')

def developer_test_notification_answer_pdf(request):
    with sudo():
        notification_answers = list(NotificationAnswer.objects.all())
    return render(request, 'developer/render_test_notification_answer_pdf.html', {'notification_answers': notification_answers})

def test_vote_pdf_html(request, vote_pk=None):
    with sudo():
        vote = get_object_or_404(Vote, pk=vote_pk)
    with sudo(vote.submission_form.submission.presenter):
        bootstrap.templates()
        template = loader.get_template('db/meetings/wkhtml2pdf/vote.html')
        html = template.render(Context(vote.get_render_context()))
    return HttpResponse(html)

def test_render_vote_pdf(request, vote_pk=None):
    with sudo():
        vote = get_object_or_404(Vote, pk=vote_pk)
    with sudo(vote.submission_form.submission.presenter):
        bootstrap.templates()
        pdf = render_pdf_context('db/meetings/wkhtml2pdf/vote.html', vote.get_render_context())
    return pdf_response(pdf, filename='test.pdf')

def developer_test_vote_pdf(request):
    with sudo():
        votes = list(Vote.objects.filter(published_at__isnull=False))
    return render(request, 'developer/render_test_vote_pdf.html', {'votes': votes})

def developer_translations(request):
    from django.contrib.auth.models import Group
    from ecs.tasks.models import TaskType

    task_types = []
    for name in sorted(list(set(TaskType.objects.all().values_list('name', flat=True)))):
        task_types.append((name, _(name)))

    return render(request, 'developer/translations.html', {
        'groups': Group.objects.all().order_by('name'),
        'task_types': task_types,
    })
