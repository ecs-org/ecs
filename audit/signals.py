# -*- coding: utf-8 -*-

import fnmatch
import re

from django.core.serializers import serialize
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from ecs.audit.models import AuditTrail
from ecs.users.utils import get_current_user, get_user


__ignored_models = ['ecs.audit.models.AuditTrail',]
if hasattr(settings, 'AUDIT_TRAIL_IGNORED_MODELS'):
    __ignored_models += list(settings.AUDIT_TRAIL_IGNORED_MODELS)

__ignored_models_rexs = [fnmatch.translate(x) for x in __ignored_models]
_ignored_models_rex = re.compile('(' + ')|('.join(__ignored_models_rexs) + ')')


def post_save_handler(**kwargs):
    """ This creates an AuditTrail entry for every db change """
    if not settings.ENABLE_AUDIT_TRAIL:  # this is set when syncdb or migrate is being run
        return
    
    sender = kwargs['sender']
    instance = kwargs['instance']
    user = get_current_user()
    if not user or not user.is_authenticated():
        user = get_user('root@example.org')

    sender_path = '.'.join([sender.__module__, sender.__name__])
    if _ignored_models_rex.match(sender_path):
        return

    description = u'%s %s instance of %s' % (
        user,
        'created' if kwargs['created'] else 'modified',
        sender.__name__,
    )

    a = AuditTrail()
    a.description = description
    a.user = user
    a.instance = instance
    a.content_type = ContentType.objects.get_for_model(sender)
    a.data = serialize('json', sender.objects.filter(pk=instance.pk))
    a.is_instance_created = kwargs['created']
    a.save()
