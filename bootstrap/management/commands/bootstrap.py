import imp, sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.utils.importlib import import_module

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
    
        # FIXME: inefficient
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
        try:
            for name in order:
                print "Bootstrapping %s." % name
                bootstrap_funcs[name]()
        except:
            transaction.rollback()
            raise
        else:
            if transaction.is_dirty():
                if dry_run:
                    transaction.rollback()
                else:
                    transaction.commit()
                    

