from django.db import models

from ecs.authorization import AuthorizationManager
from ecs.votes.constants import PERMANENT_VOTE_RESULTS, POSITIVE_VOTE_RESULTS, NEGATIVE_VOTE_RESULTS

class VoteQuerySet(models.query.QuerySet):
    def positive(self):
        return self.filter(result__in=POSITIVE_VOTE_RESULTS)
        
    def negative(self):
        return self.filter(result__in=NEGATIVE_VOTE_RESULTS)
        
    def permanent(self):
        return self.filter(result__in=PERMANENT_VOTE_RESULTS)


class VoteManager(AuthorizationManager):
    def get_base_query_set(self):
        return VoteQuerySet(self.model)

    def positive(self):
        return self.all().positive()

    def negative(self):
        return self.all().negative()

    def permanent(self):
        return self.all().permanent()
