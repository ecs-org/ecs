from django.utils.translation import ugettext as _
from ecs.communication.utils import send_system_message_template
from ecs.utils import connect
from ecs.votes import signals


@connect(signals.on_vote_publication)
def on_vote_published(sender, **kwargs):
    vote = kwargs['vote']
    if vote.submission_form:
        for p in self.submission_form.get_presenting_parties():
            if not p.user: continue
            send_system_message_template(p.user, _('Publication of {vote}').format(vote=unicode(self)), 'submissions/vote_publish.txt',
                {'vote': self, 'party': p}, submission=self.submission_form.submission)


@connect(signals.on_vote_expiry)
def on_vote_expired(sender, **kwargs):
    submission = kwargs['submission']
    submission.finish(expired=True)
