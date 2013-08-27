# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from celery.decorators import periodic_task
from celery.schedules import crontab

from ecs.votes.models import Vote
from ecs.core.models.constants import SUBMISSION_LANE_LOCALEC
from ecs.utils.common_messages import send_submission_message
from ecs.users.utils import get_office_user


def send_vote_expired(vote):
    recipients = vote.submission_form.get_presenting_parties().get_users()
    recipients.add(get_office_user())
    submission = vote.get_submission()

    url = reverse('readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    if vote.top:
        vote_date = vote.top.meeting.start
    else:
        vote_date = vote.published_at
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(vote_date)s ist abgelaufen.\n') % {
        'url': url,
        'ec_number': submission.get_ec_number_display(),
        'vote_date': vote_date.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % submission.get_ec_number_display()
    send_submission_message(submission, subject, text, recipients)

def send_vote_reminder_submitter(vote):
    recipients = vote.submission_form.get_presenting_parties().get_users()
    submission = vote.get_submission()

    url = reverse('readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    if vote.top:
        vote_date = vote.top.meeting.start
    else:
        vote_date = vote.published_at
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(vote_date)s läuft in drei Wochen ab.\n') % {
        'url': url,
        'ec_number': submission.get_ec_number_display(),
        'vote_date': vote_date.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % submission.get_ec_number_display()
    send_submission_message(submission, subject, text, recipients)
    
def send_vote_reminder_office(vote):
    recipients = [get_office_user()]
    submission = vote.get_submission()

    url = reverse('readonly_submission_form', kwargs={ 'submission_form_pk': vote.submission_form.pk })
    if vote.top:
        vote_date = vote.top.meeting.start
    else:
        vote_date = vote.published_at
    text = _(u'Das Votum für die Studie <a href="#" onclick="window.parent.location.href=\'%(url)s\';" >EK-Nr. %(ec_number)s</a> vom %(vote_date)s läuft in einer Woche ab.\n') % {
        'url': url,
        'ec_number': submission.get_ec_number_display(),
        'vote_date': vote_date.strftime('%d.%m.%Y'),
    }

    subject = _(u'Ablauf des Votums für die Studie EK-Nr. %s') % submission.get_ec_number_display()
    send_submission_message(submission, subject, text, recipients)


@periodic_task(run_every=timedelta(days=1))
def send_reminder_messages(today=None):
    if today is None:
        today = datetime.today().date()

    votes = (Vote.objects
        .filter(result='1', published_at__isnull=False, valid_until__isnull=False)
        .exclude(submission_form__submission__workflow_lane=SUBMISSION_LANE_LOCALEC)
        .exclude(submission_form__submission__is_finished=True))
    
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


@periodic_task(run_every=crontab(hour=3, minute=58))
def expire_votes():
    for vote in Vote.objects.filter(valid_until__lt=datetime.now(), is_expired=False):
        vote.expire()
