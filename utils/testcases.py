import logging
from contextlib import contextmanager

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from ecs.core import bootstrap as core_bootstrap
from ecs.mediaserver import bootstrap as mediaserver_bootstrap
from ecs.documents import bootstrap as documents_bootstrap
from ecs.users.utils import get_user, get_or_create_user


class EcsTestCase(TestCase):
    @classmethod
    def setUpClass(self):    
        core_bootstrap.templates()
        mediaserver_bootstrap.import_decryption_key()
        documents_bootstrap.import_encryption_key()
        
    @classmethod
    def teardownClass(self):
        pass
    
    def setUp(self):
        self.logger = logging.getLogger() 
        
        user, created = get_or_create_user('root@example.org', is_superuser=True)
        settings.ENABLE_AUDIT_TRAIL = True
        
        for name in "alice", "bob", "unittest":
            self.create_user(name)
        
        user = get_user('unittest@example.com')
        user.is_superuser = True
        user.save()
        
    def create_user(self, name):
        user, created = get_or_create_user('{0}@example.com'.format(name), is_superuser=True)
        user.set_password('password')
        user.save()
        profile = user.get_profile()
        profile.approved_by_office = True
        profile.save()
    
    def tearDown(self):
        settings.ENABLE_AUDIT_TRAIL = False
        User.objects.all().delete()
        
    @contextmanager
    def login(self, email, password):
        self.client.login(email=email, password=password)
        yield
        self.client.logout()



class LoginTestCase(EcsTestCase):
    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.user = get_user('unittest@example.com')
        self.client.login(email='unittest@example.com', password='password')
    
    def tearDown(self):
        super(LoginTestCase, self).tearDown()
        self.client.logout()

