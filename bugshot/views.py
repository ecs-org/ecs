# -*- coding: utf-8 -*-
import xmlrpclib, re
from base64 import b64decode
from django.http import HttpResponse, HttpResponseBadRequest

def shoot(request):
    trac = xmlrpclib.ServerProxy('https://sharing:uehkdkDijepo833@ecsdev.ep3.at/project/ecs/login/rpc')
    ticket = trac.ticket.create(request.POST.get('summary', '[bugshot]'), request.POST.get('description'), {
        "type":"bug", 
        "milestone":"Milestone 7", 
        # XXX deleted because only persons assigned to a sprint can be owner of this type of ticket "sprint":"Sprint 7", 
        "absoluteurl": request.POST.get('absoluteurl', ''),
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
        print len(data), request.POST.get('absoluteurl')
        trac.ticket.putAttachment(ticket, 'screenshot.%s' % format, 'bugshot', xmlrpclib.Binary(data))

    return HttpResponse('OK')
