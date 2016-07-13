from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from reversion.models import Version
from reversion import revisions as reversion

from ecs.votes.constants import (VOTE_RESULT_CHOICES, POSITIVE_VOTE_RESULTS, NEGATIVE_VOTE_RESULTS, PERMANENT_VOTE_RESULTS, RECESSED_VOTE_RESULTS)
from ecs.votes.managers import VoteManager
from ecs.votes.signals import on_vote_publication
from ecs.users.utils import get_current_user
from ecs.documents.models import Document
from ecs.utils.viewutils import render_pdf_context


@reversion.register(fields=('result', 'text'))
class Vote(models.Model):
    submission_form = models.ForeignKey('core.SubmissionForm', related_name='votes')
    top = models.OneToOneField('meetings.TimetableEntry', related_name='vote', null=True)
    upgrade_for = models.OneToOneField('self', null=True, related_name='previous')
    result = models.CharField(max_length=2, choices=VOTE_RESULT_CHOICES, null=True, verbose_name=_('vote'))
    executive_review_required = models.NullBooleanField(blank=True)
    text = models.TextField(blank=True, verbose_name=_('comment'))
    is_draft = models.BooleanField(default=False)
    is_final_version = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True)
    published_at = models.DateTimeField(null=True)
    published_by = models.ForeignKey('auth.User', null=True)
    valid_until = models.DateTimeField(null=True)
    changed_after_voting = models.BooleanField(default=False)
    
    objects = VoteManager()
    unfiltered = models.Manager()

    class Meta:
        get_latest_by = 'published_at'

    def get_submission(self):
        return self.submission_form.submission
    
    @property
    def result_text(self):
        # FIXME: use get_result_display instead
        if self.result is None:
            return _('No Result')
        return dict(VOTE_RESULT_CHOICES)[self.result]

    def get_ec_number(self):
        return self.submission_form.submission.get_ec_number_display()
        
    def __str__(self):
        ec_number = self.get_ec_number()
        if ec_number:
            return 'Votum %s' % ec_number
        return 'Votum ID %s' % self.pk

    def publish(self):
        assert self.published_at is None
        self.published_at = timezone.now()
        self.published_by = get_current_user()
        if self.result == '1':
            self.valid_until = self.published_at + timedelta(days=365)
        self.save()

        if not self.needs_signature:
            template = 'meetings/wkhtml2pdf/vote.html'
            pdf_data = render_pdf_context(template, self.get_render_context())

            Document.objects.create_from_buffer(pdf_data, doctype='votes',
                parent_object=self, original_file_name=self.pdf_filename,
                name=str(self))

        on_vote_publication.send(sender=Vote, vote=self)

    def expire(self):
        assert not self.is_expired
        self.is_expired = True
        self.save()

        submission = self.get_submission()
        submission.is_expired = True
        submission.save()
    
    def extend(self):
        self.valid_until += timedelta(days=365)
        self.is_expired = False
        self.save()

        submission = self.get_submission()
        submission.is_expired = False
        submission.save()

    @property
    def version_number(self):
        return Version.objects.get_for_object(self).count()
    
    @property
    def is_positive(self):
        return self.result in POSITIVE_VOTE_RESULTS
        
    @property
    def is_negative(self):
        return self.result in NEGATIVE_VOTE_RESULTS
        
    @property
    def is_permanent(self):
        return self.result in PERMANENT_VOTE_RESULTS
        
    @property
    def is_recessed(self):
        return self.result in RECESSED_VOTE_RESULTS

    @property
    def needs_signature(self):
        return self.result in ('1', '4')

    @property
    def pdf_filename(self):
        vote_name = self.get_ec_number().replace('/', '-')
        if self.top:
            top = str(self.top)
            meeting = self.top.meeting
            filename = '%s-%s-%s-vote_%s.pdf' % (meeting.title, meeting.start.strftime('%d-%m-%Y'), top, vote_name)
        else:
            filename = 'vote_%s.pdf' % (vote_name)
        return filename.replace(' ', '_')

    def get_render_context(self):
        past_votes = Vote.objects.filter(published_at__isnull=False, submission_form__submission=self.submission_form.submission).exclude(pk=self.pk).order_by('published_at')

        return {
            'vote': self,
            'submission': self.get_submission(),
            'form': self.submission_form,
            'documents': self.submission_form.documents.order_by('doctype__identifier', 'date', 'name'),
            'ABSOLUTE_URL_PREFIX': settings.ABSOLUTE_URL_PREFIX,
            'past_votes': past_votes,
        }


def _post_vote_save(sender, **kwargs):
    vote = kwargs['instance']
    submission_form = vote.submission_form
    if (vote.published_at and submission_form.current_published_vote_id == vote.pk) or (not vote.published_at and submission_form.current_pending_vote_id == vote.pk):
        return
    if vote.published_at:
        if submission_form.current_pending_vote_id == vote.pk:
            submission_form.current_pending_vote = None
        submission_form.current_published_vote = vote
    else:
        # handle Vote.submission_form changes (happens on b2 upgrades)
        submission_form.submission.forms.filter(current_pending_vote=vote).exclude(pk=submission_form.pk).update(current_pending_vote=None)
        submission_form.current_pending_vote = vote
    submission_form.save(force_update=True)

post_save.connect(_post_vote_save, sender=Vote)
