# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from ecs import authorization
from ecs.core.models.constants import (VOTE_RESULT_CHOICES, POSITIVE_VOTE_RESULTS, NEGATIVE_VOTE_RESULTS, FINAL_VOTE_RESULTS, PERMANENT_VOTE_RESULTS)

class Vote(models.Model):
    submission_form = models.ForeignKey('core.SubmissionForm', related_name='votes', null=True)
    top = models.OneToOneField('meetings.TimetableEntry', related_name='vote', null=True)
    result = models.CharField(max_length=2, choices=VOTE_RESULT_CHOICES, null=True, verbose_name=_(u'vote'))
    executive_review_required = models.NullBooleanField(blank=True)
    text = models.TextField(blank=True, verbose_name=_(u'comment'))
    is_final = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True)
    published_at = models.DateTimeField(null=True)
    valid_until = models.DateTimeField(null=True)
        
    class Meta:
        app_label = 'core'
        
    objects = authorization.AuthorizationManager()
    
    def get_submission(self):
        return self.submission_form.submission
    
    @property
    def result_text(self):
        if self.result is None:
            return _('No Result')
        return dict(VOTE_RESULT_CHOICES)[self.result]

    def get_ec_number(self):
        if self.top and self.top.submission:
            return self.top.submission.get_ec_number_display()
        elif self.submission_form:
            return self.submission_form.submission.get_ec_number_display()
        return None
        
    def __unicode__(self):
        ec_number = self.get_ec_number()
        if ec_number:
            return 'Votum %s' % ec_number
        return 'Votum ID %s' % self.pk
        
    def save(self, **kwargs):
        if not self.submission_form_id and self.top_id:
            self.submission_form = self.top.submission.current_submission_form
        return super(Vote, self).save(**kwargs)

    def publish(self):
        from ecs.communication.utils import send_system_message_template
        self.published_at = datetime.now()
        self.save()
        if self.submission_form:
            for p in self.submission_form.get_presenting_parties():
                if not p.user: continue
                send_system_message_template(p.user, _('Publication of {vote}').format(vote=unicode(self)), 'submissions/vote_publish.txt',
                    {'vote': self, 'party': p}, submission=self.submission_form.submission)
        
    @property
    def positive(self):
        return self.result in POSITIVE_VOTE_RESULTS
        
    @property
    def negative(self):
        return self.result in NEGATIVE_VOTE_RESULTS
        
    @property
    def final(self):
        return self.result in FINAL_VOTE_RESULTS
        
    @property
    def permanent(self):
        return self.result in PERMANENT_VOTE_RESULTS
        
    @property
    def recessed(self):
        return self.result in ('3a', '3b')
        
    @property
    def activates(self):
        return self.result == '1'

def _post_vote_save(sender, **kwargs):
    vote = kwargs['instance']
    submission_form = vote.submission_form
    if submission_form is None:
        return
    if (vote.published_at and submission_form.current_published_vote_id == vote.pk) or (not vote.published_at and submission_form.current_pending_vote_id == vote.pk):
        return
    if vote.published_at:
        if submission_form.current_pending_vote_id == vote.pk:
            submission_form.current_pending_vote = None
        submission_form.current_published_vote = vote
    else:
        submission_form.current_pending_vote = vote
    submission_form.save(force_update=True)

post_save.connect(_post_vote_save, sender=Vote)
