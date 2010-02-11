# ecs core views

"""
Views for ecs.
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response

import settings

from core.models import Document, Submission, NotificationForm


## helpers

def prepare(request, pagename):
    t = loader.get_template(pagename)
    d = dict(MEDIA_URL=settings.MEDIA_URL)
    c = RequestContext(request, d)
    return (t, d, c)

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
    (t, d, c) = prepare(request, 'index.html')
    return HttpResponse(t.render(c))

def submission(request, id=''):
    (t, d, c) = prepare(request, 'submission.html')
    return HttpResponse(t.render(c))

# notification form

def notification_new1(request):
    # added to request:
    #   submission -> set of submission.id
    #   notificationtype -> [0..4]  
    if request.method == 'POST' and request.POST.has_key('notificationtype'):
        # process
        # TODO validate input
        if request.POST.has_key('submission'):
            submission = request.POST['submission']
        else:
            # no submission selected
            # TODO clarify where to check and what to do
            return HttpResponseRedirect(reverse('ecs.core.views.notification_new1'))            
        notificationtype = request.POST['notificationtype']
        # TODO seems to be GET only
        return HttpResponseRedirect(reverse('ecs.core.views.notification_new2'))
    else:
        # get last active submission
        id = 1  # TODO get last active submission from DB
        code = 'EK-343/2009'
        form_last_active_submission = {'id': id, 'code': code}
        # get this user's active submissions
        form_submissions = []  # TODO Submission.objects.filter(user = this_user)
        submissions = Submission.objects.all()
        for submission in submissions:
            id = submission.id
            code = 'EK-{0}/2010'.format(id)  # TODO get code from DB
            form_submissions.append({'id': id, 'code': code})
        # render template
        pagename = 'notification_new01.html'
        t = loader.get_template(pagename)
        d = dict(MEDIA_URL = settings.MEDIA_URL, 
                 last_active_submission = form_last_active_submission, 
                 submissions = form_submissions)
        c = RequestContext(request, d)
        return HttpResponse(t.render(c))

def notification_new2(request):
    # added to request:
    #   protocolnumber -> string
    #   statement -> string (html)
    if request.method == 'POST' and request.POST.has_key('protocolnumber'):
        # process
        # TODO validate input (or not)
        return HttpResponseRedirect(reverse('ecs.core.views.notification_new3'))
    else:
        # get protocol number
        protocolnumber = 'P12345'  # TODO get this from submission
        # get statement
        statement = ''  # TODO clarify 
        # render template
        pagename = 'notification_new02.html'
        t = loader.get_template(pagename)
        d = dict(MEDIA_URL = settings.MEDIA_URL,  # TODO put back prior request vars into request
                 protocolnumber = protocolnumber,
                 statement = statement)
        c = RequestContext(request, d)
        return HttpResponse(t.render(c))

def notification_new3(request):
    # added to request:
    #   doctype -> [0..8]
    #   description -> string
    #   versiondate -> date
    #   fileupload -> file
    if request.method == 'POST' and request.POST.has_key('doctype'):
        # process
        # TODO validate input (or not)
        # TODO slam all what we have collected so far into the DB

        # store uploaded file (if supplied)
        if request.FILES['fileupload']:
            fileupload = request.FILES['fileupload']
            if fileupload.size == 0:
                return HttpResponse('Die Datei ' + fileupload.name + ' ist leer!')
            uuid = file_uuid(fileupload)
            uuid_revision = uuid   # TODO explain this field
            description = request.POST['description']  # TODO harmonize IDs Form, DB
            versiondate = request.POST['versiondate']
            document = Document(uuid_document = uuid, 
                                uuid_document_revision = uuid_revision,
                                version = description,
                                date = versiondate,
                                absent = False)
            fileupload.seek(0)  # rewind because of prior hashing
            dest = document.open('w')
            s = fileupload.read()
            dest.write(s)
            dest.close()
            document.save()
        return HttpResponseRedirect(reverse('ecs.core.views.index'))
    else:
        # get existing docs
        form_docs = []
        # render template
        pagename = 'notification_new03.html'
        t = loader.get_template(pagename)
        d = dict(MEDIA_URL = settings.MEDIA_URL,
                 docs = form_docs)
        c = RequestContext(request, d)
        return HttpResponse(t.render(c))


def create_new_notification(request):
    return HttpResponse("Hello World!")

