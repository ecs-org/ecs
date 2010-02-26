# ecs core views

"""
Views for ecs.
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader, Template
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list

import settings

from ecs.core.models import Document, Notification, BaseNotificationForm, NotificationType, Submission, InvolvedCommissionsForNotification
from ecs.core.forms import DocumentUploadForm
from ecs.utils.htmldoc import htmldoc

## helpers

def render(request, template, context):
    if not isinstance(template, Template):
        template = loader.get_template(template)
    return HttpResponse(template.render(RequestContext(request, context)))

def file_uuid(doc_file):
    """returns md5 digest of a given file as uuid"""
    import hashlib
    s = doc_file.read()  # TODO optimize for large files! check if correct for binary files (e.g. random bytes)
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

## views

def demo(request):
    return render_to_response('demo-django.html')

def index(request):
    return render(request, 'index.html', {})

def submission(request, id=''):
    return render(request, 'submission.html', {})
    
# documents
def download_document(request, document_pk=None):
    doc = get_object_or_404(Document, pk=document_pk)
    response = HttpResponse(doc.file, content_type=doc.mimetype)
    response['Content-Disposition'] = 'attachment;filename=document_%s.pdf' % doc.pk
    return response
    

# notification form
def view_notification(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    return render(request, 'notifications/view.html', {
        'notification': notification,
    })

def select_notification_creation_type(request):
    return render(request, 'notifications/select_creation_type.html', {
        'notification_types': NotificationType.objects.order_by('name')
    })

def create_notification(request, notification_type_pk=None):
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    if request.method == 'POST':
        form = notification_type.form_cls(request.POST)
        if form.is_valid():
            notification_form = form.save(commit=False)
            notification_form.type = notification_type
            notification_form.notification = Notification.objects.create()
            notification_form.save()
            for ethics_commission in form.cleaned_data['ethics_commissions']:
                InvolvedCommissionsForNotification.objects.create(commission=ethics_commission, submission=notification_form, main=False)
            notification_form.submission_forms = form.cleaned_data['submission_forms']
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification_form.notification.pk}))
    else:
        form = notification_type.form_cls()
    return render(request, 'notifications/create.html', {
        'notification_type': notification_type,
        'form': form,
    })


def upload_document_for_notification(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    documents = notification.documents.all()
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            # FIXME: this should be handled by the file storage system on the fly.
            document.uuid_document = file_uuid(document.file)
            document.uuid_document_revision = document.uuid_document
            document.file.seek(0)
            document.save()
            notification.documents.add(document)
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification.pk}))
    else:
        form = DocumentUploadForm()
    return render(request, 'notifications/upload_document.html', {
        'notification': notification,
        'documents': documents,
        'form': form,
    })


def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(BaseNotificationForm, pk=notification_pk)
    template_names = ['notifications/htmldoc/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    tpl = loader.select_template(template_names)
    html = tpl.render(Context({
        'notification': notification,
        'url': request.build_absolute_uri(),
    }))
    pdf = htmldoc(html.encode('ISO-8859-1'), webpage=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=notification_%s.pdf' % notification_pk
    return response

def submissiondetail(request, submissionid):
    submission = Submission.objects.get(id=int(submissionid))
    notifications = Notification.objects.filter(submission=submission)
    if submission:
        return object_list(request, queryset=notifications)
    return HttpResponse("BOOM")
