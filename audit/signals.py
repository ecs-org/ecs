# -*- coding: utf-8 -*-

from django.core.serializers import serialize
from django.conf import settings

from ecs.audit.models import AuditTrail
from ecs.users.utils import get_current_user

def post_save_handler(**kwargs):
    if not settings.ENABLE_AUDIT_TRAIL:
        return

    ignore_list = [
        'ecs.audit.models.AuditTrail',
    ]
    
    if hasattr(settings, 'AUDIT_TRAIL_IGNORED_MODELS'):
        ignore_list += list(settings.AUDIT_TRAIL_IGNORED_MODELS)
    
    ignored_models = set()
    for entry in ignore_list:
        entry_list = entry.split('.')
        module = __import__('.'.join(entry_list[:-1]), fromlist=entry_list[:-2])
        ignored_model = getattr(module, entry_list[-1])
        ignored_models.add(ignored_model)
    
    
    sender = kwargs['sender']
    instance = kwargs['instance']
    
    if sender in ignored_models:
        return

    description = '%s %s instance of %s' % (
        get_current_user(),
        'created' if kwargs['created'] else 'modified',
        sender.__name__,
    )

    a = AuditTrail()
    a.description = description
    a.instance = instance
    a.data = serialize('json', sender.objects.filter(pk=instance.pk))
    a.save()
