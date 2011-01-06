from django.core.management import call_command
from ecs import bootstrap
from ecs import workflow

@bootstrap.register()
def workflow_sync():
    workflow.autodiscover()
    call_command('workflow_sync', quiet=True)


