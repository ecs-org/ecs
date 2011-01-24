# -*- coding: utf-8 -*-

import os
from subprocess import list2cmdline

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        call_command('makemessages', all=True)
        editor = os.environ.get('EDITOR', 'vi')
        locale_file = os.path.join(settings.PROJECT_DIR, 'locale', 'de', 'LC_MESSAGES', 'django.po')
        os.system(list2cmdline([editor, locale_file]))
        call_command('compilemessages')

