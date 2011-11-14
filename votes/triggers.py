from django.utils.translation import ugettext as _
from django.conf import settings
from ecs.communication.utils import send_system_message_template
from ecs.utils import connect
from ecs.votes import signals


@connect(signals.on_vote_publication)
def on_vote_published(sender, **kwargs):
    vote = kwargs['vote']
    if vote.submission_form and not vote.submission_form.is_categorized_multicentric_and_local:
        parties = vote.submission_form.get_presenting_parties()
        parties.send_message(_('Publication of {vote}').format(vote=unicode(vote)), 'submissions/vote_publish.txt',
            {'vote': vote}, submission=vote.submission_form.submission, cc_groups=settings.ECS_VOTE_RECEIVER_GROUPS)

@connect(signals.on_vote_expiry)
def on_vote_expiry(sender, **kwargs):
    print "vote expired", kwargs
    submission = kwargs['submission']
    submission.finish(expired=True)
