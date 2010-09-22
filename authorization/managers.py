from django.db import models
from ecs.users.utils import get_current_user
from ecs.authorization.base import make_q_factory

class AuthorizationManager(models.Manager):
    def __init__(self, prefix=None, **kwargs):
        self.prefix = prefix
        super(AuthorizationManager, self).__init__(**kwargs)

    def get_q_factory(self):
        if not hasattr(self, '_q_factory'):
            self._q_factory = make_q_factory(self.model, self.prefix)
        return self._q_factory

    def get_query_set(self):
        qs = super(AuthorizationManager, self).get_query_set()
        q_factory = self.get_q_factory()
        user = get_current_user()
        if not user or not q_factory:
            return qs
        return qs.filter(q_factory(user))
