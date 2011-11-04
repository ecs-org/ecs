# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from ecs.workflow import Activity, guard, register
from ecs.users.utils import sudo
from ecs.votes.models import Vote
from ecs.tasks.models import Task

def vote_workflow_start_if(vote, created):
    return vote.result and (not vote.top_id or vote.top.meeting.ended) and not vote.workflow

register(Vote, autostart_if=vote_workflow_start_if)

@guard(model=Vote)
def is_executive_vote_review_required(wf):
    return wf.data.executive_review_required

@guard(model=Vote)
def is_final(wf):
    return wf.data.is_final_version

@guard(model=Vote)
def is_b2(wf):
    return wf.data.result == '2'

@guard(model=Vote)
def is_b2upgrade(wf):
    previous_vote = wf.data.submission_form.votes.filter(pk__lt=wf.data.pk).order_by('-pk')[:1]
    return wf.data.activates and previous_vote and previous_vote[0].result == '2'

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
        return reverse('ecs.votes.views.readonly_submission_form', kwargs={'submission_form_pk': self.workflow.data.submission_form_id})

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

