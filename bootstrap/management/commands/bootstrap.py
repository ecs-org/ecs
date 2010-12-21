# -*- coding: utf-8 -*-
import imp, sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.auth.models import User

from ecs.audit.models import AuditTrail
from ecs.users.utils import get_or_create_user

def _create_root_user():
    settings.ENABLE_AUDIT_LOG = False
    root, _ = get_or_create_user('root@system')
    root.first_name = 'System'
    root.last_name = 'Administrator'
    root.is_staff = True
    root.is_superuser = True
    root.set_unusable_password()
    root.save()
    settings.ENABLE_AUDIT_LOG = True


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--dry-run', dest='dry_run', action='store_true', default=False, help="Don't change the db, just output what would be done"),
    )

    @transaction.commit_manually
    def handle(self, dry_run=False, **options):
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
        
        def log_save(sender, **kwargs):
            if sender == AuditTrail:  # dont log creation of audit trail entries
                return
            obj = kwargs['instance']
            model = obj.__class__
            action = kwargs.get('created', False) and "Create" or "Update"
            print "    %s %s.%s pk=%s" % (action, model._meta.app_label, model.__name__, obj.pk)

        def log_delete(sender, **kwargs):
            obj = kwargs['instance']
            model = obj.__class__
            print "    Delete %s.%s pk=%s" % (model._meta.app_label, model.__name__, obj.pk)


        post_save.connect(log_save)
        post_delete.connect(log_delete)

        def cleanup(rollback=False):
            post_save.disconnect(log_save)
            post_delete.disconnect(log_delete)
            if rollback:
                transaction.rollback()
            else:
                transaction.commit()

        try:
            _create_root_user()
            for name in order:
                print "Bootstrapping %s." % name
                func = bootstrap_funcs[name]
                func()
        except:
            cleanup(rollback=True)
            raise
        else:
            if transaction.is_dirty():
                cleanup(rollback=True if dry_run else False)

