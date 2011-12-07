from django.db import models
from ecs.authorization.managers import AuthorizationManager


class NotificationQuerySet(models.query.QuerySet):
    def answered(self):
        return self.filter(models.Q(answer__isnull=False) | models.Q(safetynotification__is_acknowledged=True))
        
    def unanswered(self):
        return self.filter(models.Q(answer__isnull=True) & (models.Q(safetynotification__isnull=True) | models.Q(safetynotification__is_acknowledged=False)))


class NotificationManager(AuthorizationManager):
    def get_base_query_set(self):
        return NotificationQuerySet(self.model)

    def answered(self):
        return self.all().answered()

    def unanswered(self):
        return self.all().unanswered()
