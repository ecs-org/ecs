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
    for workdir in (settings.LOGFILE_DIR, settings.TEMPFILE_DIR, settings.GENFILE_DIR, settings.INCOMING_FILESTORE):
        if not os.path.isdir(workdir):
            os.makedirs(workdir)

@bootstrap.register()
def compilemessages():
    #call_command('compilemessages')
    pass # disabled for now, because the gettext install for windows is not right yet
