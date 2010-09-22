from django.db import models
from django.core.exceptions import ImproperlyConfigured
from ecs.users.utils import get_current_user
from ecs.authorization.base import get_q_factory

class AuthorizationManager(models.Manager):
    def get_q_factory(self):
        if not hasattr(self, '_q_factory'):
            self._q_factory = get_q_factory(self.model)
        return self._q_factory

    def get_query_set(self):
        qs = super(AuthorizationManager, self).get_query_set()
        user = get_current_user()
        if not user:
            return qs
        q_factory = self.get_q_factory()
        return qs.filter(q_factory(user))
