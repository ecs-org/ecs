import datetime

from django.core.management.base import BaseCommand, CommandError

from ecs.workflow.models import Token


class Command(BaseCommand):
    def handle(self, **options):
        deadline_tokens = Token.objects.filter(consumed_at=None, deadline__lt=datetime.datetime.now())
        for token in deadline_tokens:
            token.handle_deadline()
