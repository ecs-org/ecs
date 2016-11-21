from django.db import models
from django.db.models import Q

from ecs.authorization.managers import AuthorizationManager


class NotificationQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(Q(answer=None) | Q(answer__published_at=None))


NotificationManager = AuthorizationManager.from_queryset(NotificationQuerySet)
