from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from ecs.core.models import Submission
from ecs.checklists.models import Checklist
from ecs.core import paper_forms
from ecs.utils.viewutils import render_pdf_context, pdf_response
from ecs.users.utils import sudo
from ecs.notifications.models import Notification, NotificationAnswer
from ecs.votes.models import Vote
from ecs.utils.decorators import developer

@developer
def test_pdf_html(request, submission_pk=None):
    with sudo():
        submission = get_object_or_404(Submission, pk=submission_pk)
    with sudo(submission.presenter):
        submission_form = submission.current_submission_form
        template = loader.get_template('submissions/wkhtml2pdf/view.html')
        html = template.render({
            'paper_form_fields': paper_forms.get_field_info_for_model(submission_form.__class__),
            'submission_form': submission_form,
            'documents': submission_form.documents.order_by('doctype__identifier', 'date', 'name'),
        })
    return HttpResponse(html)

@developer
def test_render_pdf(request, submission_pk=None):
    with sudo():
        submission = get_object_or_404(Submission, pk=submission_pk)
    with sudo(submission.presenter):
        submission_form = submission.current_submission_form
        pdf = render_pdf_context('submissions/wkhtml2pdf/view.html', {
            'paper_form_fields': paper_forms.get_field_info_for_model(submission_form.__class__),
            'submission_form': submission_form,
            'documents': submission_form.documents.order_by('doctype__identifier', 'date', 'name'),
        })
    return pdf_response(pdf, filename='test.pdf')

@developer
def developer_test_pdf(request):
    with sudo():
        submissions = list(Submission.objects.all().order_by('ec_number'))
    return render(request, 'developer/render_test_pdf.html', {'submissions': submissions})

@developer
def test_checklist_pdf_html(request, checklist_pk=None):
    with sudo():
        checklist = get_object_or_404(Checklist, pk=checklist_pk)
    with sudo(checklist.user):
        template = loader.get_template('checklists/wkhtml2pdf/checklist.html')
        html = template.render({'checklist': checklist})
    return HttpResponse(html)

@developer
def test_render_checklist_pdf(request, checklist_pk=None):
    with sudo():
        checklist = get_object_or_404(Checklist, pk=checklist_pk)
    with sudo(checklist.user):
        pdf = render_pdf_context('checklists/wkhtml2pdf/checklist.html', {
            'checklist': checklist,
        })
    return pdf_response(pdf, filename='test.pdf')

@developer
def developer_test_checklist_pdf(request):
    with sudo():
        checklists = list(Checklist.objects.all().order_by('submission__ec_number', 'blueprint__name'))
    return render(request, 'developer/render_test_checklist_pdf.html', {'checklists': checklists})

@developer
def test_notification_pdf_html(request, notification_pk=None):
    with sudo():
        notification = get_object_or_404(Notification, pk=notification_pk)
    with sudo(notification.user):
        tpl = notification.type.get_template('notifications/wkhtml2pdf/%s.html')
        submission_forms = notification.submission_forms.select_related('submission').all()
        html = tpl.render({
            'notification': notification,
            'submission_forms': submission_forms,
            'documents': notification.documents.order_by('doctype__identifier', 'date', 'name'),
        })
    return HttpResponse(html)

@developer
def test_render_notification_pdf(request, notification_pk=None):
    with sudo():
        notification = get_object_or_404(Notification, pk=notification_pk)
    with sudo(notification.user):
        tpl = notification.type.get_template('notifications/wkhtml2pdf/%s.html')
        submission_forms = notification.submission_forms.select_related('submission').all()
        pdf = render_pdf_context(tpl, {
            'notification': notification,
            'submission_forms': submission_forms,
            'documents': notification.documents.order_by('doctype__identifier', 'date', 'name'),
        })
    return pdf_response(pdf, filename='test.pdf')

@developer
def developer_test_notification_pdf(request):
    with sudo():
        notifications = list(Notification.objects.all())
    return render(request, 'developer/render_test_notification_pdf.html', {'notifications': notifications})

@developer
def test_notification_answer_pdf_html(request, notification_answer_pk=None):
    with sudo():
        notification_answer = get_object_or_404(NotificationAnswer, pk=notification_answer_pk)
    with sudo(notification_answer.notification.user):
        notification = notification_answer.notification
        tpl = notification.type.get_template('notifications/answers/wkhtml2pdf/%s.html')
        html = tpl.render({
            'notification': notification,
            'documents': notification.documents.order_by('doctype__identifier', 'date', 'name'),
            'answer': notification_answer
        })
    return HttpResponse(html)

@developer
def test_render_notification_answer_pdf(request, notification_answer_pk=None):
    with sudo():
        notification_answer = get_object_or_404(NotificationAnswer, pk=notification_answer_pk)
    with sudo(notification_answer.notification.user):
        notification = notification_answer.notification
        tpl = notification.type.get_template('notifications/answers/wkhtml2pdf/%s.html')
        pdf = render_pdf_context(tpl, {
            'notification': notification,
            'documents': notification.documents.order_by('doctype__identifier', 'date', 'name'),
            'answer': notification_answer
        })
    return pdf_response(pdf, filename='test.pdf')

@developer
def developer_test_notification_answer_pdf(request):
    with sudo():
        notification_answers = list(NotificationAnswer.objects.all())
    return render(request, 'developer/render_test_notification_answer_pdf.html', {'notification_answers': notification_answers})

@developer
def test_vote_pdf_html(request, vote_pk=None):
    with sudo():
        vote = get_object_or_404(Vote, pk=vote_pk)
    with sudo(vote.submission_form.submission.presenter):
        template = loader.get_template('meetings/wkhtml2pdf/vote.html')
        html = template.render(vote.get_render_context())
    return HttpResponse(html)

@developer
def test_render_vote_pdf(request, vote_pk=None):
    with sudo():
        vote = get_object_or_404(Vote, pk=vote_pk)
    with sudo(vote.submission_form.submission.presenter):
        pdf = render_pdf_context('meetings/wkhtml2pdf/vote.html', vote.get_render_context())
    return pdf_response(pdf, filename='test.pdf')

@developer
def developer_test_vote_pdf(request):
    with sudo():
        votes = list(Vote.objects.filter(published_at__isnull=False))
    return render(request, 'developer/render_test_vote_pdf.html', {'votes': votes})

@developer
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
