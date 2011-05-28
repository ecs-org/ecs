# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from ecs import authorization

VOTE_RESULT_CHOICES = (
    ('1', _(u'1 positive')),
    ('1a', _(u'1a positive - with corrections')),
    ('2', _(u'2 positive under reserve')),
    ('3', _(u'3 recessed (objections)')),
    ('4', _(u'4 negative')),
    ('5', _(u'5 recessed (applicant)')),
    ('5a', _(u'5a withdrawn (applicant)')),
    ('5b', _(u'5b not examined')),
    #('5c', _(u'5c Lokale EK')),
)

POSITIVE_VOTE_RESULTS = ('1', '1a', '2')
NEGATIVE_VOTE_RESULTS = ('4', '5a')
FINAL_VOTE_RESULTS = POSITIVE_VOTE_RESULTS + NEGATIVE_VOTE_RESULTS


class Vote(models.Model):
    submission_form = models.ForeignKey('core.SubmissionForm', related_name='votes', null=True)
    top = models.OneToOneField('meetings.TimetableEntry', related_name='vote', null=True)
    result = models.CharField(max_length=2, choices=VOTE_RESULT_CHOICES, null=True, verbose_name=_(u'vote'))
    executive_review_required = models.NullBooleanField(blank=True)
    text = models.TextField(blank=True, verbose_name=_(u'comment'))
    is_final = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True)
    published_at = models.DateTimeField(null=True)
        
    class Meta:
        app_label = 'core'
        
    objects = authorization.AuthorizationManager()
    
    def get_submission(self):
        return self.submission_form.submission
    
    @property
    def result_text(self):
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
    def recessed(self):
        return self.result in ('3', '5', '5b')
        
    @property
    def activates(self):
        return self.result in ('1', '1a')


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
