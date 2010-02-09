# ecs core views

"""
Views for ecs.
"""

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response

import settings

from core.models import NotificationForm


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

def notification_new1(request):
    (t, d, c) = prepare(request, 'notification_new01.html')
    return HttpResponse(t.render(c))

def notification_new2(request):
    (t, d, c) = prepare(request, 'notification_new02.html')
    return HttpResponse(t.render(c))

def notification_new3(request):
    (t, d, c) = prepare(request, 'notification_new03.html')
    return HttpResponse(t.render(c))

def create_new_notification(request):
    return "Hello World!"

def notification_new4(request):
    (t, d, c) = prepare(request, 'index.html')
    notificationform = NotificationForm()
    notificationform.save()        
    return HttpResponse(t.render(c))

