from django.db import models

from ecs.authorization import AuthorizationManager
from ecs.votes.constants import PERMANENT_VOTE_RESULTS, POSITIVE_VOTE_RESULTS, NEGATIVE_VOTE_RESULTS, RECESSED_VOTE_RESULTS


class VoteQuerySet(models.QuerySet):
    def positive(self):
        return self.filter(result__in=POSITIVE_VOTE_RESULTS)
        
    def negative(self):
        return self.filter(result__in=NEGATIVE_VOTE_RESULTS)
        
    def permanent(self):
        return self.filter(result__in=PERMANENT_VOTE_RESULTS)

    def recessed(self):
        return self.filter(result__in=RECESSED_VOTE_RESULTS)


VoteManager = AuthorizationManager.from_queryset(VoteQuerySet)
