# -*- coding: utf-8 -*-
import xmlrpclib, re
from base64 import b64decode
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

def shoot(request):
    trac = xmlrpclib.ServerProxy(settings.BUGSHOT_CONFIG['bugshoturl'])
    
    component = ""
    if request.POST.get('component', ''):
        try:
            componentnr = trac.ticket.component.get(request.POST.get('component', ''))
            component = request.POST.get('component', '')
        except xmlrpclib.Fault:
            return HttpResponseBadRequest("invalid component %s" % request.POST.get('component', ''))

    priority = "normal"
    if request.POST.get('priority', ''):
        try:
            prioritynr = trac.ticket.priority.get(request.POST.get('priority', ''))
            priority = request.POST.get('priority', '')
        except xmlrpclib.Fault:
            return HttpResponseBadRequest("invalid priority %s" % request.POST.get('priority', ''))

    if hasattr(request, "original_user"):
        bugshot_reporter = request.original_user.__unicode__() 
    else:
        bugshot_reporter = request.user.__unicode__()
    
    ticket = trac.ticket.create(request.POST.get('summary', '[bugshot]'), request.POST.get('description'), {
        "type":"bug", 
        "owner": request.POST.get('owner', ''),
        "priority": priority,
        "component": component,
        "milestone": settings.BUGSHOT_CONFIG['milestone'], 
        "bugshot_reporter": bugshot_reporter,
        "absoluteurl": request.POST.get('url', ''),
    }, True)

    dataurl = request.POST.get('image', None)
    if dataurl:
        head, data = dataurl.split(',', 1)
        match = re.match('data:image/(png|jpg);base64', head)
        if not match:
            return HttpResponseBadRequest("invalid data url: only base64 encoded image/png and image/jpg data will be accepted")
        format = match.group(1)
        try:
            data = b64decode(data)
        except TypeError:
            return HttpResponseBadRequest("invalid base64 data")
        print len(data), request.POST.get('url')
        trac.ticket.putAttachment(ticket, 'screenshot.%s' % format, 'bugshot', xmlrpclib.Binary(data))

    return HttpResponse('OK')
