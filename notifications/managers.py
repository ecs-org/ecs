from django.db import models
from ecs.authorization.managers import AuthorizationManager


def _get_answer_q():
    return models.Q(answer__isnull=False) | models.Q(safetynotification__is_acknowledged=True)


class NotificationQuerySet(models.query.QuerySet):
    def answered(self):
        return self.filter(_get_answer_q())
        
    def unanswered(self):
        return self.exclude(_get_answer_q())


class NotificationManager(AuthorizationManager):
    def get_query_set(self):
        return NotificationQuerySet(self.model)

    def answered(self):
        return self.all().answered()

    def unanswered(self):
        return self.all().unanswered()
