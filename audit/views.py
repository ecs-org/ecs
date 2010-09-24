# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404

from ecs.utils.viewutils import render, render_html
from ecs.audit.models import AuditTrail


def log(request, format):
    entries = AuditTrail.objects.all().order_by('created_at')
    if format == 'html':
        template = 'audit/log.html'
        mimetype = 'text/html'
    elif format == 'txt':
        template = 'audit/log.txt'
        mimetype = 'text/plain'
    else:
        raise Http404()
    
    return render(request, template, {
        'entries': entries,
    }, mimetype=mimetype)

