# -*- coding: utf-8 -*-
import imp
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.utils.importlib import import_module

from ecs.users.utils import get_or_create_user

def _create_root_user():
    root, _ = get_or_create_user('root@system.local')
    root.first_name = ''
    root.last_name = 'Ethik-Kommission'
    root.is_staff = True
    root.is_superuser = True
    root.set_unusable_password() # root (System) is not supposed to login
    root.save()
    
    profile = root.get_profile()
    profile.forward_messages_after_minutes = 0 # Never forward messages
    profile.gender = 'x'
    profile.save()


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, **options):
        bootstrap_funcs = {}
        for app in settings.INSTALLED_APPS:
            try:
                app_path = import_module(app).__path__
            except AttributeError:
                continue
            try:
                imp.find_module('bootstrap', app_path)
            except ImportError:
                continue
            module = import_module("%s.bootstrap" % app)
            for name in dir(module):
                if name.startswith('_'):
                    continue
                func = getattr(module, name)
                if callable(func) and getattr(func, 'bootstrap', False):
                    bootstrap_funcs["%s.%s" % (func.__module__, func.__name__)] = func

        # XXX: inefficient (FMD3)
        cycle = True
        order = []
        while len(order) < len(bootstrap_funcs):
            cycle = True
            for name, func in bootstrap_funcs.iteritems():
                if name not in order and set(order) >= set(func.depends_on):
                    order.append(name)
                    cycle = False
            if cycle:
                raise CommandError("Cyclic dependencies: %s" % ", ".join(sorted(set(bootstrap_funcs.keys())-set(order))))
        
        _create_root_user()
        for name in order:
            print ' > {0}'.format(name)
            func = bootstrap_funcs[name]
            func()
