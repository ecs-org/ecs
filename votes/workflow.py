# -*- coding: utf-8 -*-
from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ecs.workflow import Activity, guard, register
from ecs.users.utils import sudo
from ecs.votes.models import Vote
from ecs.tasks.models import Task


def vote_workflow_start_if(vote, created):
    # iff all of the following conditions are true:
    # - there is a result
    # - it's either not been in a meeting or the meeting has ended
    # - its workflow hasn't been started already
    # - it's not a draft (vote preparation)
    return vote.result and (not vote.top_id or vote.top.meeting.ended) and not vote.workflow and not vote.is_draft

register(Vote, autostart_if=vote_workflow_start_if)


@guard(model=Vote)
def is_executive_vote_review_required(wf):
    return wf.data.executive_review_required

@guard(model=Vote)
def is_final(wf):
    return wf.data.is_final_version


class VoteFinalization(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        return reverse('ecs.core.views.vote_review', kwargs={'submission_form_pk': self.workflow.data.submission_form_id})


class VoteReview(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        return reverse('ecs.core.views.vote_review', kwargs={'submission_form_pk': self.workflow.data.submission_form_id})


class VoteSigning(Activity):
    class Meta:
        model = Vote

    def pre_perform(self, choice):
        vote = self.workflow.data
        vote.publish()

    def get_url(self):
        return reverse('ecs.votes.views.vote_sign', kwargs={'vote_pk': self.workflow.data.pk})


class VoteB2Review(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        return reverse('readonly_submission_form', kwargs={'submission_form_pk': self.workflow.data.submission_form_id})

    def get_choices(self):
        return (
            ('1', _('B1')),
            ('3b', _('B3')),
        )

    def pre_perform(self, choice):
        sf = self.workflow.data.submission_form
        new_vote = Vote.objects.create(submission_form=sf, result=choice)
        if new_vote.is_permanent:
            # abort all tasks
            with sudo():
                open_tasks = Task.objects.for_data(sf.submission).filter(deleted_at__isnull=True, closed_at=None)
                for task in open_tasks:
                    task.deleted_at = datetime.now()
                    task.save()
        if choice == '3b':
            sf.submission.schedule_to_meeting()


class B2Resubmission(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        s = self.workflow.data.submission_form.submission
        return reverse('ecs.core.views.copy_latest_submission_form', kwargs={'submission_pk': s.pk})

    def get_final_urls(self):
        s = self.workflow.data.submission_form.submission
        return super(B2Resubmission, self).get_final_urls() + [
            reverse('readonly_submission_form', kwargs={'submission_form_pk': sf})
            for sf in s.forms.values_list('pk', flat=True)
        ]

    def receive_token(self, *args, **kwargs):
        token = super(B2Resubmission, self).receive_token(*args, **kwargs)
        token.task.assign(self.workflow.data.submission_form.submission.presenter)
        return token
