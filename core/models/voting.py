# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from ecs.authorization.managers import AuthorizationManager

VOTE_RESULT_CHOICES = (
    ('1', u'1 Positiv'),
    ('1a', u'1a Positiv - mit Ausbesserungen'),
    ('2', u'2 Vorbehaltich positiv'),
    ('3', u'3 Vertagt (Einwände)'),
    ('4', u'4 Negativ'),
    ('5', u'5 Vertagt (Antragsteller)'),
    ('5a', u'5a Zurückgezogen (Antragsteller)'),
    ('5b', u'5b Nicht behandelt'),
    #('5c', u'5c Lokale EK'),
)

POSITIVE_VOTE_RESULTS = ('1', '1a', '2')
NEGATIVE_VOTE_RESULTS = ('4', '5a')
FINAL_VOTE_RESULTS = POSITIVE_VOTE_RESULTS + NEGATIVE_VOTE_RESULTS


class Vote(models.Model):
    submission_form = models.ForeignKey('core.SubmissionForm', related_name='votes')
    top = models.OneToOneField('meetings.TimetableEntry', related_name='vote', null=True)
    result = models.CharField(max_length=2, choices=VOTE_RESULT_CHOICES, null=True, verbose_name=u'Votum')
    executive_review_required = models.NullBooleanField(blank=True)
    text = models.TextField(blank=True, verbose_name=u'Kommentar')
    published = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'core'
        
    objects = AuthorizationManager('submission_form__submission')

    def get_ec_number(self):
        if self.top:
            top = self.top
            if top.submission:
                submission = top.submission
                if submission.ec_number:
                    ec_number = submission.ec_number
                    return ec_number
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
    if (vote.published and submission_form.current_published_vote_id == vote.pk) or (not vote.published and submission_form.current_pending_vote_id == vote.pk):
        return
    if vote.published:
        if submission_form.current_pending_vote_id == vote.pk:
            submission_form.current_pending_vote = None
        submission_form.current_published_vote = vote
    else:
        submission_form.current_pending_vote = vote
    submission_form.save(force_update=True)

post_save.connect(_post_vote_save, sender=Vote)
