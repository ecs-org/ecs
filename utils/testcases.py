from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from ecs.core import bootstrap

class EcsTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username="root", is_superuser=True)
        settings.ENABLE_AUDIT_TRAIL = True
        bootstrap.templates()
    
    def tearDown(self):
        settings.ENABLE_AUDIT_TRAIL = False
        User.objects.all().delete()

class LoginTestCase(EcsTestCase):
    def setUp(self):
        super(LoginTestCase, self).setUp()
        user = User(username='unittest', is_superuser=True)
        user.set_password('password')
        user.save()
        profile = user.get_profile()
        profile.approved_by_office = True
        profile.save()
        self.user = user
        self.client.login(username='unittest', password='password')
    
    def tearDown(self):
        super(LoginTestCase, self).tearDown()
        self.client.logout()

            