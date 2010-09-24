# -*- coding: utf-8 -*-

from django.http import Http404
from django.contrib.auth.decorators import user_passes_test

from ecs.utils.viewutils import render, render_html
from ecs.audit.models import AuditTrail


@user_passes_test(lambda u: u.ecs_profile.executive_board_member)
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

