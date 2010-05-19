import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from ecs.workflow.models import NodeType, Guard, NODE_TYPE_CATEGORY_ACTIVITY, NODE_TYPE_CATEGORY_CONTROL

def _get_ct_or_none(model):
    if model:
        return ContentType.objects.get_for_model(model)
    return None
    
def _format_model(model):
    if model:
        return "model %s.%s" % (model.__module__, model.__name__)
    return "all models"

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--dry-run', dest='dry-run', action='store_true', default=False, help="Don't change the db, just output what would be done"),
        make_option('--quiet', dest='quiet', action='store_true', default=False, help="Suppress any output")
    )

    def handle(self, **options):
        if options['dry-run']:
            self.do_dryrun(**options)
        else:
            self.do_sync(**options)

    @transaction.commit_manually
    def do_dryrun(self, **options):
        try:
            self.do_sync(**options)
        finally:
            transaction.rollback()
    
    def do_sync(self, quiet=False, **options):
        from ecs.workflow.controller import registry
        guards = set()
        for handler in registry.guards:
            guard, created = Guard.objects.get_or_create(
                implementation=handler.name, 
                content_type=_get_ct_or_none(handler.model), 
                defaults={'name': handler.name}
            )
            guards.add(guard)
            registry._guard_map[guard.pk] = handler
            if created and not quiet:
                print "Created guard '%s' for %s" % (handler.name, _format_model(handler.model))

        Guard.objects.exclude(pk__in=[g.pk for g in guards]).delete()

        node_types = set()
        for handler in registry.activities:
            node_type, created = NodeType.objects.get_or_create(
                category=NODE_TYPE_CATEGORY_ACTIVITY, 
                implementation=handler.name, 
                content_type=_get_ct_or_none(handler.model), 
                defaults={'name': handler.name, 'data_type': _get_ct_or_none(handler.vary_on)}
            )
            node_types.add(node_type)
            registry._node_type_map[node_type.pk] = handler
            if created and not quiet:
                print "Created activity '%s' for %s" % (handler.name, _format_model(handler.model))

        for handler in registry.controls:
            node_type, created = NodeType.objects.get_or_create(
                category=NODE_TYPE_CATEGORY_CONTROL,
                implementation=handler.name,
                content_type=_get_ct_or_none(handler.model),
                defaults={'name': handler.name, 'data_type': _get_ct_or_none(handler.vary_on)}
            )
            node_types.add(node_type)
            registry._node_type_map[node_type.pk] = handler
            if created and not quiet:
                print "Created control '%s' for %s" % (handler.name, _format_model(handler.model))
        NodeType.objects.exclude(pk__in=[nt.pk for nt in node_types]).delete()
