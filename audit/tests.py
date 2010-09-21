# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User

from ecs.utils.testcases import TestCase
from ecs.audit.models import AuditTrail

import time

class AuditTrailCase(TestCase):
    def setUp(self):  # FIXME: insane hack
        self.enable_audit_trail = getattr(settings, 'ENABLE_AUDIT_TRAIL', None)
        self.root_exists = User.objects.filter(username='root').exists()
        if not self.root_exists:
            settings.ENABLE_AUDIT_TRAIL = False
            User.objects.create(username='root')
        settings.ENABLE_AUDIT_TRAIL = True
    
    def tearDown(self):
        if not self.root_exists:
            settings.ENABLE_AUDIT_TRAIL = False
            User.objects.get(username='root').delete()
        if self.enable_audit_trail is None:
            del settings.ENABLE_AUDIT_TRAIL
        else:
            settings.ENABLE_AUDIT_TRAIL = self.enable_audit_trail

class SettingsTest(AuditTrailCase):
    def test_settings(self):
        self.failUnless(hasattr(settings, 'ENABLE_AUDIT_TRAIL'))
        self.failUnless(hasattr(settings, 'AUDIT_TRAIL_IGNORED_MODELS'))
           
class CreateUserTest(AuditTrailCase):
    def test_create_user(self):
        audit_trail_entries_count = AuditTrail.objects.count()
        User.objects.create(username='audit_trail_test_user')  # User and UserProfile are being created
        self.failUnlessEqual(audit_trail_entries_count+2, AuditTrail.objects.count())
