# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from celery.decorators import periodic_task

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.votes.models import Vote
from ecs.meetings.models import Meeting
from ecs.core.models import Submission
from ecs.utils.common_messages import send_submission_message
from ecs.votes.signals import on_vote_expiry



def send_vote_expired(vote):
    recipients_q = Q(email=settings.ECSMAIL['postmaster'])
    if vote.submission_form.submitter:
        recipients_q |= Q(pk=vote.submission_form.submitter.pk)
    if vote.submission_form.submitter_email:
        recipients_q |= Q(email=vote.submission_form.submitter_email)

    recipients = User.objects.filter(recipients_q)

    url = reverse('readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(meeting_date)s ist abgelaufen.\n') % {
        'url': url,
        'ec_number': vote.submission_form.submission.get_ec_number_display(),
        'meeting_date': vote.top.meeting.start.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % vote.submission_form.submission.get_ec_number_display()
    send_submission_message(vote.submission_form.submission, subject, text, recipients)

def send_vote_reminder_submitter(vote):
    recipients = User.objects.none()
    if vote.submission_form.submitter:
        recipients |= User.objects.filter(pk=vote.submission_form.submitter.pk)
    if vote.submission_form.submitter_email:
        recipients |= User.objects.filter(email=vote.submission_form.submitter_email)

    url = reverse('readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(meeting_date)s läuft in drei Wochen ab.\n') % {
        'url': url,
        'ec_number': vote.submission_form.submission.get_ec_number_display(),
        'meeting_date': vote.top.meeting.start.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % vote.submission_form.submission.get_ec_number_display()
    send_submission_message(vote.submission_form.submission, subject, text, recipients)
    
def send_vote_reminder_office(vote):
    recipients = User.objects.filter(email=settings.ECSMAIL['postmaster'])

    url = reverse('readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(meeting_date)s läuft in einer Woche ab.\n') % {
        'url': url,
        'ec_number': vote.submission_form.submission.get_ec_number_display(),
        'meeting_date': vote.top.meeting.start.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % vote.submission_form.submission.get_ec_number_display()
    send_submission_message(vote.submission_form.submission, subject, text, recipients)


@periodic_task(run_every=timedelta(days=1))
def send_reminder_messages(today=None):
    if today is None:
        today = datetime.today().date()

    votes = Vote.objects.filter(result='1', published_at__isnull=False, valid_until__isnull=False)
    for vote in votes:
        valid_until = vote.valid_until.date()
        if today < valid_until:
            days_valid = (valid_until - today).days
        else:
            days_valid = 0 - (today - valid_until).days

        if days_valid == 21:
            send_vote_reminder_submitter(vote)
        elif days_valid == 7:
            send_vote_reminder_office(vote)
        elif days_valid == -1:
            send_vote_expired(vote)

@periodic_task(run_every=timedelta(minutes=1))
def expire_votes():
    for submission in Submission.objects.filter(is_finished=False).with_vote(positive=True, permanent=True, published=True, valid=None, valid_until__lte=datetime.now()):
        on_vote_expiry.send(Vote, submission=submission)
