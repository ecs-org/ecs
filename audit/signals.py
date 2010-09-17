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
        'django.contrib.sessions.models.Session',
    ]
    
    ignored_classes = set()
    for entry in ignore_list:
        entry_list = entry.split('.')
        module = __import__('.'.join(entry_list[:-1]), fromlist=entry_list[:-2])
        ignored_class = getattr(module, entry_list[-1])
        ignored_classes.add(ignored_class)
    
    
    sender = kwargs['sender']
    instance = kwargs['instance']
    
    if sender in ignored_classes:
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
