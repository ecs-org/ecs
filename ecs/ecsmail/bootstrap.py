import os
   
from django.conf import settings
from ecs import bootstrap

@bootstrap.register()
def create_undeliverable_queue_dir():
    basedir = settings.ECSMAIL ['undeliverable_queue_dir']

    if not os.path.isdir(basedir):
        os.makedirs(basedir, mode=0722)
    
    for node in ("tmp", "new", "cur"):
        nodedir = os.path.join(basedir, node)
        if not os.path.isdir(nodedir):
            os.mkdir(nodedir, 0700)