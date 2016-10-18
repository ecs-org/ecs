from django.core.urlresolvers import reverse

from ecs.workflow import Activity, guard, register
from ecs.votes.models import Vote
from ecs.core.models import AdvancedSettings


def vote_workflow_start_if(vote, created):
    # iff all of the following conditions are true:
    # - there is a result
    # - it's either not been in a meeting or the meeting has ended
    # - its workflow hasn't been started already
    # - it's not a draft (vote preparation)
    return vote.result and (not vote.top_id or vote.top.meeting.ended) and not vote.workflow and not vote.is_draft

register(Vote, autostart_if=vote_workflow_start_if)


@guard(model=Vote)
def is_final(wf):
    return wf.data.is_final_version


@guard(model=Vote)
def internal_vote_review_required(wf):
    s = AdvancedSettings.objects.get()
    return s.require_internal_vote_review


class VoteReview(Activity):
    class Meta:
        model = Vote

    def is_repeatable(self):
        return True

    def get_url(self):
        return reverse('ecs.core.views.submissions.vote_review', kwargs={'submission_form_pk': self.workflow.data.submission_form_id})

    def receive_token(self, source, trail=(), repeated=False):
        token = super().receive_token(source, trail=trail, repeated=repeated)
        if trail:
            token.task.review_for = trail[0].task
            token.task.save()
        return token


class VoteSigning(Activity):
    class Meta:
        model = Vote

    def get_choices(self):
        return (
            (True, 'ok', 'success'),
            (False, 'pushback', 'warning'),
        )

    def pre_perform(self, choice):
        vote = self.workflow.data
        if choice:
            vote.publish()

    def get_url(self):
        return reverse('ecs.votes.views.vote_sign', kwargs={'vote_pk': self.workflow.data_id})

    def receive_token(self, source, trail=(), repeated=False):
        vote = trail[0].workflow.data
        if vote.needs_signature:
            return super().receive_token(source, trail=trail, repeated=repeated)
        else:
            vote.publish()
