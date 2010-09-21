# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User

from ecs.utils.testcases import EcsTestCase
from ecs.audit.models import AuditTrail

import time

class SettingsTest(EcsTestCase):
    def test_settings(self):
        self.failUnless(hasattr(settings, 'ENABLE_AUDIT_TRAIL'))
        self.failUnless(hasattr(settings, 'AUDIT_TRAIL_IGNORED_MODELS'))
           
class CreateUserTest(EcsTestCase):
    def test_create_user(self):
        audit_trail_entries_count = AuditTrail.objects.count()
        User.objects.create(username='audit_trail_test_user')  # User and UserProfile are being created
        self.failUnlessEqual(audit_trail_entries_count+2, AuditTrail.objects.count())
