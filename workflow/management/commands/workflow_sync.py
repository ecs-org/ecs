import datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

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
    def handle(self, **options):
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
            if created:
                print "Created guard '%s' for %s" % (handler.name, _format_model(handler.model))

        Guard.objects.exclude(pk__in=[g.pk for g in guards]).delete()

        node_types = set()
        for handler in registry.activities:
            node_type, created = NodeType.objects.get_or_create(
                category=NODE_TYPE_CATEGORY_ACTIVITY, 
                implementation=handler.name, 
                content_type=_get_ct_or_none(handler.model), 
                defaults={'name': handler.name}
            )
            node_types.add(node_type)
            registry._node_type_map[node_type.pk] = handler
            if created:
                print "Created activity '%s' for %s" % (handler.name, _format_model(handler.model))

        for handler in registry.controls:
            node_type, created = NodeType.objects.get_or_create(
                category=NODE_TYPE_CATEGORY_CONTROL,
                implementation=handler.name,
                content_type=_get_ct_or_none(handler.model),
                defaults={'name': handler.name}
            )
            node_types.add(node_type)
            registry._node_type_map[node_type.pk] = handler
            if created:
                print "Created control '%s' for %s" % (handler.name, _format_model(handler.model))
        NodeType.objects.exclude(pk__in=[nt.pk for nt in node_types]).delete()
