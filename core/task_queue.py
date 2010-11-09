# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from celery.decorators import periodic_task

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.core.models import Vote
from ecs.meetings.models import Meeting
from ecs.utils.common_messages import send_submission_message

def send_vote_expired(vote):
    recipients_q = Q(username=settings.ECSMAIL['postmaster'])
    if vote.submission_form.submitter:
        recipients_q |= Q(pk=vote.submission_form.submitter.pk)
    if vote.submission_form.submitter_email:
        recipients_q |= Q(email=vote.submission_form.submitter_email)

    recipients = User.objects.filter(recipients_q)

    url = reverse('ecs.core.views.readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(meeting_date)s ist abgelaufen.\n') % {
        'url': url,
        'ec_number': vote.submission_form.submission.get_ec_number_display(),
        'meeting_date': vote.top.meeting.start.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % vote.submission_form.submission.get_ec_number_display()
    send_submission_message(vote.submission_form.submission, subject, text, recipients, username='root')

def send_vote_reminder_submitter(vote):
    recipients = User.objects.none()
    if vote.submission_form.submitter:
        recipients |= User.objects.filter(pk=vote.submission_form.submitter.pk)
    if vote.submission_form.submitter_email:
        recipients |= User.objects.filter(email=vote.submission_form.submitter_email)

    url = reverse('ecs.core.views.readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(meeting_date)s läuft in drei Wochen ab.\n') % {
        'url': url,
        'ec_number': vote.submission_form.submission.get_ec_number_display(),
        'meeting_date': vote.top.meeting.start.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % vote.submission_form.submission.get_ec_number_display()
    send_submission_message(vote.submission_form.submission, subject, text, recipients, username='root')
    
def send_vote_reminder_office(vote):
    recipients = User.objects.filter(username=settings.ECSMAIL['postmaster'])

    url = reverse('ecs.core.views.readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(meeting_date)s läuft in einer Woche ab.\n') % {
        'url': url,
        'ec_number': vote.submission_form.submission.get_ec_number_display(),
        'meeting_date': vote.top.meeting.start.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % vote.submission_form.submission.get_ec_number_display()
    send_submission_message(vote.submission_form.submission, subject, text, recipients, username='root')


@periodic_task(run_every=timedelta(days=1))
def send_reminder_messages():
    votes = Vote.objects.filter(Q(_currently_pending_for__isnull=False, _currently_pending_for__current_for_submission__isnull=False)|Q(_currently_published_for__isnull=False, _currently_published_for__current_for_submission__isnull=False), result='2')
    for vote in votes:
        try:
            until_meeting = Meeting.objects.filter(start__gt=vote.top.meeting.start).order_by('start')[2]
        except IndexError:
            continue
        
        deadline = until_meeting.deadline  # FIXME: use the other deadline for thesis
        now = datetime.now()

        if now < deadline:
            days_until_deadline = (deadline - now).days
        else:
            days_until_deadline = 0 - (now - deadline).days

        if days_until_deadline == 21:
            send_vote_reminder_submitter(vote)
        elif days_until_deadline == 7:
            send_vote_reminder_office(vote)
        elif days_until_deadline == -1:
            send_vote_expired(vote)
        else:
            continue


