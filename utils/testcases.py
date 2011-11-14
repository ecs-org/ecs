import logging
from contextlib import contextmanager

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from ecs.integration import bootstrap as integration_bootstrap
from ecs.core import bootstrap as core_bootstrap
from ecs.mediaserver import bootstrap as mediaserver_bootstrap
from ecs.documents import bootstrap as documents_bootstrap
from ecs.checklists import bootstrap as checklists_bootstrap
from ecs.users.utils import get_user, get_or_create_user


class EcsTestCase(TestCase):
    @classmethod
    def setUpClass(self):
        get_or_create_user('root@example.org', is_superuser=True)
        get_or_create_user(settings.DEFAULT_CONTACT)
        
        integration_bootstrap.create_settings_dirs()
        
        core_bootstrap.templates()
        documents_bootstrap.document_types()

        mediaserver_bootstrap.import_encryption_sign_keys()
        mediaserver_bootstrap.import_decryption_verify_keys()
        mediaserver_bootstrap.create_disk_caches()
        mediaserver_bootstrap.create_local_storage_vault()

        integration_bootstrap.workflow_sync()
        core_bootstrap.auth_groups()
        checklists_bootstrap.checklist_blueprints()
        core_bootstrap.submission_workflow()
        
    @classmethod
    def teardownClass(self):
        pass
    
    def setUp(self):
        self.logger = logging.getLogger() 

        settings.ENABLE_AUDIT_TRAIL = True
        
        self.create_user('alice', profile_extra={'is_internal': True})
        for name in ('bob', 'unittest',):
            self.create_user(name)
        
        user = get_user('unittest@example.com')
        user.is_superuser = True
        user.save()
        
    def create_user(self, name, extra=None, profile_extra=None):
        extra = extra or {}
        profile_extra = profile_extra or {}
        user, created = get_or_create_user('{0}@example.com'.format(name), is_superuser=True, **extra)
        user.set_password('password')
        user.save()
        profile = user.get_profile()
        for k, v in profile_extra.iteritems():
            setattr(profile, k, v)
        profile.is_approved_by_office = True
        profile.save()
        return user
    
    def tearDown(self):
        settings.ENABLE_AUDIT_TRAIL = False
        User.objects.all().delete()
        
    @contextmanager
    def login(self, email, password='password'):
        if '@' not in email:
            email = '{0}@example.com'.format(email)
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

