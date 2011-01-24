# -*- coding: utf-8 -*-
from ecs import bootstrap
from django.core import management

@bootstrap.register()
def createinitialrevisions():
    management.call_command('createinitialrevisions', 'help.Page', verbosity=2, interactive=False)
