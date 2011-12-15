from datetime import datetime, timedelta
from celery.decorators import periodic_task
from ecs.workflow.models import Token
from ecs import workflow

workflow.autodiscover()

@periodic_task(run_every=timedelta(minutes=1))
def handle_deadlines():
    deadline_tokens = Token.objects.filter(consumed_at=None, deadline__lt=datetime.now())
    for token in deadline_tokens:
        token.handle_deadline()
