# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.conf import settings

from ecs.audit.signals import post_save_handler

# (in)sanity check
if not hasattr(settings, 'ENABLE_AUDIT_TRAIL'):
    print 'WARNING: ENABLE_AUDIT_TRAIL is absent from the settings; audit trail is'
    print '         disabled! Please write "ENABLE_AUDIT_TRAIL=False" into the settings'
    print '         if this behaviour is intended.'
    settings.ENABLE_AUDIT_TRAIL = False

post_save.connect(post_save_handler)
