from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from ecs.core import bootstrap

class EcsTestCase(TestCase):
    @classmethod
    def setUpClass(self):    
        bootstrap.templates()
        
    @classmethod
    def teardownClass(self):
        pass
    
    def setUp(self):
        user = User.objects.create(username="root", email = "root@example.org", is_superuser=True)
        settings.ENABLE_AUDIT_TRAIL = True
        
        for name in "alice", "bob", "unittest":
            user = User(username=name, is_superuser=True)
            user.email = "".join((name, "@example.org"))
            user.set_password('password')
            user.save()
            profile = user.get_profile()
            profile.approved_by_office = True
            profile.save()
        
        user = User.objects.get(username = "unittest")
        user.is_superuser = True
        user.save()
    
    def tearDown(self):
        settings.ENABLE_AUDIT_TRAIL = False
        User.objects.all().delete()


class LoginTestCase(EcsTestCase):
    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.user = User.objects.get(username="unittest")
        self.client.login(username='unittest', password='password')
    
    def tearDown(self):
        super(LoginTestCase, self).tearDown()
        self.client.logout()

            