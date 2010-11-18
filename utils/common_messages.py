# -*- coding: utf-8 -*-
'''
Created on Sep 27, 2010

@author: amir
'''
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

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
    nr = sf.submission.get_ec_number_display()
    text = _(u'The study EC-Nr. %s was created.\n' % nr )
    url = reverse('ecs.core.views.readonly_submission_form', kwargs={ 'submission_form_pk': sf.pk })
    text += _(u'Click <a href="#" onclick="window.parent.location.href=\'%s\';">here</a> to view it.' % url )
    subject = _(u'New study EC-Nr. %s' % nr )
    send_submission_message(sf.submission, subject, text, registered_recipients, username=username)
    
def send_submission_invitation(sf, unregistered_recipients, username='root'):
    nr = sf.submission.get_ec_number_display()
    text = _(u'The study EC-Nr. %s was created.\n' % nr )
    url = reverse('ecs.users.views.register')
    text += _(u'Please register <a href="#" onclick="window.parent.location.href=\'%s\';">here</a> to view the study.' % url )
    subject = _(u'New study EC-Nr. %s' % nr )
    send_submission_message(sf.submission, subject, text, unregistered_recipients, username=username)

def send_submission_change(old_sf, new_sf, recipients, username='root'):
    newnr = new_sf.submission.get_ec_number_display()
    text = _(u'Changes were made to study EC-Nr. %s.\n' % newnr)
    url = reverse('ecs.core.views.diff', kwargs={'old_submission_form_pk': old_sf.pk, 'new_submission_form_pk': new_sf.pk})
    text += _(u'Click <a href="#" onclick="window.parent.location.href=\'%s\';">here</a> to view it.' % url)
    subject = _(u'Changes to study EC-Nr. %s' % newnr)
    send_submission_message(new_sf.submission, subject, text, recipients, username=username)
