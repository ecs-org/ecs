from django.core.urlresolvers import reverse

from ecs.workflow import Activity, guard, register
from ecs.votes.models import Vote


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


class VoteReview(Activity):
    class Meta:
        model = Vote

    def is_repeatable(self):
        return True

    def get_url(self):
        return reverse('ecs.core.views.submissions.vote_review', kwargs={'submission_form_pk': self.workflow.data.submission_form_id})


class VoteSigning(Activity):
    class Meta:
        model = Vote

    def get_choices(self):
        return (
            (True, 'ok'),
            (False, 'pushback'),
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
            return super(VoteSigning, self).receive_token(
                source, trail=trail, repeated=repeated)
        else:
            vote.publish()


class B2Resubmission(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        submission_id = self.workflow.data.submission_form.submission_id
        return reverse('ecs.core.views.submissions.copy_latest_submission_form', kwargs={'submission_pk': submission_id})

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


### to be removed
class VoteB2Review(Activity):
    class Meta:
        model = Vote


### to be removed
class VoteFinalization(Activity):
    class Meta:
        model = Vote
