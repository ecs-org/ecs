# -*- coding: utf-8 -*-

import os

from django.core.management.base import BaseCommand
from django.core.management.commands.compilemessages import compile_messages

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        os.system('./manage.py makemessages -a')
        try:
            editor = os.environ['EDITOR']
        except KeyError:
            editor = 'vi'
        os.system('%s locale/de/LC_MESSAGES/django.po' % editor)
        compile_messages()

