# ecs core views

"""
Views for ecs.
"""

from django.http import HttpResponse
from django.template import RequestContext, loader
import settings

def index(request):
    t = loader.get_template('index.html')
    d = dict(MEDIA_URL=settings.MEDIA_URL)
    c = RequestContext(request, d)
    return HttpResponse(t.render(c))

def submission(request, id=''):
    t = loader.get_template('submission.html')
    d = dict(MEDIA_URL=settings.MEDIA_URL)
    c = RequestContext(request, d)
    return HttpResponse(t.render(c))

def notification(request, id=''):
    t = loader.get_template('notification.html')
    d = dict(MEDIA_URL=settings.MEDIA_URL)
    c = RequestContext(request, d)
    return HttpResponse(t.render(c))



