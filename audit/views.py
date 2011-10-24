# -*- coding: utf-8 -*-

from datetime import datetime
import time

from django.http import Http404

from ecs.utils.viewutils import render, render_html
from ecs.audit.models import AuditTrail
from ecs.users.utils import user_flag_required


@user_flag_required('is_executive_board_member')
def log(request, format, limit=50, until=None, since=None):
    if format == 'html':
        template = 'audit/log.html'
        mimetype = 'text/html'
    elif format == 'txt':
        template = 'audit/log.txt'
        mimetype = 'text/plain'
    else:
        raise Http404()

    limit = int(limit)

    if until is not None:
        until = int(until)
        entries = list(AuditTrail.objects.filter(pk__lte=until).order_by('-pk')[:limit])

    elif since is not None:
        since = int(since)
        entries = list(AuditTrail.objects.filter(pk__gte=since).order_by('pk')[:limit])
        entries.reverse()

    else:
        entries = list(AuditTrail.objects.all().order_by('-pk')[:limit])

    first_entry = entries[-1]
    last_entry = entries[0]

    try:
        previous_entry = AuditTrail.objects.filter(pk__lt=first_entry.pk).order_by('-pk')[0]
    except IndexError:
        previous_pk = None
    else:
        previous_pk = previous_entry.pk

    try:
        next_entry = AuditTrail.objects.filter(pk__gt=last_entry.pk).order_by('pk')[0]
    except IndexError:
        next_pk = None
    else:
        next_pk = next_entry.pk

    return render(request, template, {
        'entries': entries,
        'previous_pk': previous_pk,
        'next_pk': next_pk,
        'limit': limit,
    }, mimetype=mimetype)

