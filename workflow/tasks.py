import datetime
from celery.decorators import task
from ecs.workflow.models import Token

@task
def handle_deadlines():
    deadline_tokens = Token.objects.filter(consumed_at=None, deadline__lt=datetime.datetime.now())
    for token in deadline_tokens:
        token.handle_deadline()
