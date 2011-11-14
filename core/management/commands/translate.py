# -*- coding: utf-8 -*-

import os
import sys
from subprocess import list2cmdline

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        is_win = sys.platform == 'win32'
        editor = os.environ.get('EDITOR', 'notepad' if is_win else 'vi')
        if is_win:      # path hack for gettext
            os.environ['PATH'] = '{0}\\bin;{1}'.format(os.environ['VIRTUAL_ENV'], os.environ['PATH'])
        call_command('makemessages', all=True, extensions=['html', 'inc', 'txt'])
        locale_file = os.path.join(settings.PROJECT_DIR, 'locale', 'de', 'LC_MESSAGES', 'django.po')
        os.system(list2cmdline([editor, locale_file]))
        call_command('compilemessages')
