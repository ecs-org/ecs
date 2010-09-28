# -*- coding: utf-8 -*-
'''
Created on Sep 27, 2010

@author: elchaschab
'''
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from ecs.communication.models import Thread

def send_submission_message(submission, subject, text, recipients, username='root'):
    for recipient in recipients:
        thread, created = Thread.objects.get_or_create(
            subject=subject,
            sender=User.objects.get(username=username),
            receiver=recipient,
            submission=submission
        )
        message = thread.add_message(User.objects.get(username=username), text=text)

def send_submission_creation(sf, registered_recipients, username='root'):
    text = u'Die Studie EK-Nr. %s wurde angelegt.\n' % (sf.submission.ec_number)
    url = reverse('ecs.core.views.view_submission_form', kwargs={ 'submission_form_pk': sf.pk })
    text += u'Um sie anzusehen klicken sie <a href="#" onclick="window.parent.location.href=\'%s\';">hier</a>.' % (url)
    subject = u'Neue Studie EK-Nr. %s' % (sf.submission.ec_number)
    send_submission_message(sf.submission, subject, text, registered_recipients, username=username)
    
def send_submission_invitation(sf, unregistered_recipients, username='root'):
    text = u'Die Studie EK-Nr. %s wurde angelegt.\n' % (sf.submission.ec_number)
    url = reverse('ecs.core.views.register')
    text += u'Bitte registrieren sie sich <a href="#" onclick="window.parent.location.href=\'%s\';">hier</a>, um die Studie einzusehen' % (url)
    subject = u'Neue Studie EK-Nr. %s' % (sf.submission.ec_number)
    send_submission_message(sf.submission, subject, text, unregistered_recipients, username=username)

def send_submission_change(sf, recipients, username='root'):
    text = u'An der Studie EK-Nr. %s wurden Änderungen durchgeführt.\n' % sf.submission.ec_number
    url = reverse('ecs.core.views.diff', kwargs={'old_submission_form_pk': sf.pk, 'new_submission_form_pk': sf.pk})
    text += u'Um sie anzusehen klicken sie <a href="#" onclick="window.parent.location.href=\'%s\';">hier</a>.' % url
    subject = u'Änderungen an %s' % sf.submission.ec_number
    send_submission_message(sf.submission, subject, text, recipients, username=username)
