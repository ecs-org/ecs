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
        from ecs.workflow.controllers.registry import iter_guards, iter_activities, iter_controls
        guards = set()
        for g in iter_guards():
            guard, created = Guard.objects.get_or_create(
                implementation=g._meta.name, 
                content_type=_get_ct_or_none(g._meta.model), 
                defaults={'name': g._meta.name}
            )
            guards.add(guard)
            if created and not quiet:
                print "Created guard '%s' for %s" % (g._meta.name, _format_model(g._meta.model))

        for removed_guard in Guard.objects.exclude(pk__in=[g.pk for g in guards]):
            print "The implementation for Guard '%s' could not be found, but it is still present in the db." % removed_guard.implementation

        node_types = set()
        for a in iter_activities():
            node_type, created = NodeType.objects.get_or_create(
                category=NODE_TYPE_CATEGORY_ACTIVITY, 
                implementation=a._meta.name, 
                content_type=_get_ct_or_none(a._meta.model), 
                defaults={'name': a._meta.name, 'data_type': _get_ct_or_none(a._meta.vary_on)}
            )
            node_types.add(node_type)
            if created and not quiet:
                print "Created activity '%s' for %s" % (a._meta.name, _format_model(a._meta.model))

        for c in iter_controls():
            node_type, created = NodeType.objects.get_or_create(
                category=NODE_TYPE_CATEGORY_CONTROL,
                implementation=c._meta.name,
                content_type=_get_ct_or_none(c._meta.model),
                defaults={'name': c._meta.name, 'data_type': _get_ct_or_none(c._meta.vary_on)}
            )
            node_types.add(node_type)
            if created and not quiet:
                print "Created control '%s' for %s" % (c._meta.name, _format_model(c._meta.model))
        
        for removed_node_type in NodeType.objects.exclude(pk__in=[nt.pk for nt in node_types]):
            if not removed_node_type.is_subgraph:
                print "The implementation for NodeType '%s' could not be found, but it is still present in the db." % removed_node_type.implementation
            
