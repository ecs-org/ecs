# ecs core views

"""
Views for ecs.
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response

import settings

from core.models import Submission, NotificationForm


def demo(request):
    return render_to_response('demo-django.html')


def prepare(request, pagename):
    t = loader.get_template(pagename)
    d = dict(MEDIA_URL=settings.MEDIA_URL)
    c = RequestContext(request, d)
    return (t, d, c)

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

    return HttpResponse(t.render(c))

def notification_new3(request):
    (t, d, c) = prepare(request, 'notification_new03.html')
    return HttpResponse(t.render(c))

def create_new_notification(request):
    return "Hello World!"

