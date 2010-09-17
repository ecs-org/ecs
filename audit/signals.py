# -*- coding: utf-8 -*-

from django.core.serializers import serialize
from django.conf import settings

from ecs.audit.models import AuditTrail
from ecs.users.utils import get_current_user

def post_save_handler(**kwargs):
    sender = kwargs['sender']
    instance = kwargs['instance']
    
    if sender == AuditTrail:
        return
    
    if not settings.ENABLE_AUDIT_TRAIL:
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
