import os

from django.conf import settings
from django.core.management import call_command

from ecs import bootstrap
from ecs import workflow

@bootstrap.register()
def workflow_sync():
    workflow.autodiscover()
    call_command('workflow_sync', quiet=True)

@bootstrap.register()
def create_settings_dirs():
    os.makedirs(settings.ECS_DOWNLOAD_CACHE_DIR, exist_ok=True)

@bootstrap.register()
def compilemessages():
    call_command('compilemessages')
