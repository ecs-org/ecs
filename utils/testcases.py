from django.test import TestCase
from django.contrib.auth.models import User

from django.conf import settings

class EcsTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="root", is_superuser=True)
        settings.ENABLE_AUDIT_TRAIL = True
    
    def tearDown(self):
        settings.ENABLE_AUDIT_TRAIL = False
        User.objects.all().delete()

class LoginTestCase(EcsTestCase):
    def setUp(self):
        super(LoginTestCase, self).setUp()
        user = User(username='unittest')
        user.set_password('password')
        user.save()
        self.client.login(username='unittest', password='password')
    
    def tearDown(self):
        super(LoginTestCase, self).tearDown()
        self.client.logout()
