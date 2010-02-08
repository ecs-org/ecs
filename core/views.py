# ecs core views

"""
Views for ecs.
"""

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response

import settings

def index(request):
    t = loader.get_template('index.html')
    d = dict(MEDIA_URL=settings.MEDIA_URL_CORE)
    c = RequestContext(request, d)
    return HttpResponse(t.render(c))

def submission(request, id=''):
    t = loader.get_template('submission.html')
    d = dict(MEDIA_URL=settings.MEDIA_URL_CORE)
    c = RequestContext(request, d)
    return HttpResponse(t.render(c))

def notification_new1(request):
    t = loader.get_template('notification_new1.html')
    d = dict(MEDIA_URL=settings.MEDIA_URL_CORE)
    c = RequestContext(request, d)
    return HttpResponse(t.render(c))

def notification_new2(request):
    t = loader.get_template('notification_new2.html')
    d = dict(MEDIA_URL=settings.MEDIA_URL_CORE)
    c = RequestContext(request, d)
    return HttpResponse(t.render(c))

def notification_new3(request):
    t = loader.get_template('notification_new3.html')
    d = dict(MEDIA_URL=settings.MEDIA_URL_CORE)
    c = RequestContext(request, d)
    return HttpResponse(t.render(c))


def demo(request):
    return render_to_response('demo-django.html')
