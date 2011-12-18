import os

from django.conf import settings

from ecs import bootstrap

@bootstrap.register()
def create_undeliverable_queue_dir():
    workdir = settings.ECSMAIL ['undeliverable_queue_dir']
    if not os.path.isdir(workdir):
        os.makedirs(workdir, mode=0722)
    