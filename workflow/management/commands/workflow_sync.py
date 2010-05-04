import datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from ecs.workflow.models import NodeType, Guard

class Command(BaseCommand):
    def handle(self, **options):
        from ecs.workflow.controller import _guards, _activities, _controls, _guard_map, _node_type_map
        guards = set()
        for model, handlers in _guards.iteritems():
            ct = ContentType.objects.get_for_model(model)
            for name, handler in handlers.iteritems():
                guard, created = Guard.objects.get_or_create(condition=name, content_type=ct)
                guards.add(guard)
                _guard_map[guard.pk] = handler
                handler.obj = guard

        Guard.objects.exclude(pk__in=[g.pk for g in guards]).delete()

        node_types = set()
        for model, activities in _activities.iteritems():
            ct = ContentType.objects.get_for_model(model)
            for name, activity in activities.iteritems():
                node_type, created = NodeType.objects.get_or_create(
                    is_activity=True, 
                    controller=name, 
                    content_type=ct, 
                    defaults={'name': name}
                )
                node_types.add(node_type)
                _node_type_map[node_type.pk] = activity
                activity.node_type = node_type

        for name, handler in _controls.iteritems():
            node_type, created = NodeType.objects.get_or_create(
                is_activity=False,
                controller=name,
                content_type=None,
                defaults={'name': name}
            )
            node_types.add(node_type)
            _node_type_map[node_type.pk] = handler
            handler.node_type = node_type
        NodeType.objects.exclude(pk__in=[nt.pk for nt in node_types]).delete()
