# -*- coding: utf-8 -*-

from ecs.audit.models import AuditTrail

def post_save_handler(**kwargs):
    if kwargs['sender'] == AuditTrail:
        return

    if kwargs['created']:
        print 'Instance %s created' % kwargs['instance']
    else:
        print 'Instance %s modified' % kwargs['instance']

