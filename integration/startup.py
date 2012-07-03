import os
import logging
from sentry.client.handlers import SentryHandler

from ecs import workflow
from ecs.integration.django_workarounds import workaround_16759


def _patch_django():
    workaround_16759()
    
# patch the get_score method, so fallback for non postgres,mysql works (S instead of s)
def _patch_sentry_GroupedMessage_get_score():
    def _GroupedMessage_get_score(self):
        import math
        return int(math.log(self.times_seen) * 600 + int(self.last_seen.strftime('%S')))

    from sentry.models import GroupedMessage
    GroupedMessage.get_score = _GroupedMessage_get_score


def startup():
    _patch_django()

    workflow.autodiscover() # discover workflow items

    import ecs.core.triggers
    import ecs.votes.triggers
    import ecs.notifications.triggers
    import ecs.documents.triggers
    import ecs.meetings.triggers

    # configure logging

    logger = logging.getLogger()
    # ensure we havent already registered the handler
    if SentryHandler not in map(lambda x: x.__class__, logger.handlers):
        logger.addHandler(SentryHandler())

    # Add StreamHandler to sentry's default so you can catch missed exceptions
    #logger = logging.getLogger('sentry.errors')
    #logger.propagate = False
    #logger.addHandler(logging.StreamHandler())

    _patch_sentry_GroupedMessage_get_score()
