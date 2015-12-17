import logging
import tempfile
import shutil
from contextlib import contextmanager

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ecs.integration import bootstrap as integration_bootstrap
from ecs.core import bootstrap as core_bootstrap
from ecs.documents import bootstrap as documents_bootstrap
from ecs.checklists import bootstrap as checklists_bootstrap
from ecs.users.utils import get_user, get_or_create_user
from ecs.workflow.controllers import clear_caches as clear_workflow_caches


class EcsTestCase(TestCase):
    @classmethod
    def setUpClass(self):
        ContentType.objects.clear_cache()
        clear_workflow_caches()

        get_or_create_user('root@system.local', is_superuser=True)

        settings.STORAGE_VAULT_DIR = tempfile.mkdtemp()
        
        integration_bootstrap.create_settings_dirs()
        
        core_bootstrap.auth_groups()
        core_bootstrap.expedited_review_categories()
        core_bootstrap.medical_categories()
        core_bootstrap.auth_user_testusers()
        core_bootstrap.advanced_settings()

        documents_bootstrap.document_types()
        documents_bootstrap.import_encryption_sign_keys()
        documents_bootstrap.import_decryption_verify_keys()
        documents_bootstrap.create_local_storage_vault()

        integration_bootstrap.workflow_sync()
        core_bootstrap.auth_groups()
        checklists_bootstrap.checklist_blueprints()
        core_bootstrap.submission_workflow()
        
    @classmethod
    def teardownClass(self):
        shutil.rmtree(settings.STORAGE_VAULT_DIR)
    
    def setUp(self):
        self.logger = logging.getLogger() 
        
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
        profile = user.profile
        for k, v in profile_extra.iteritems():
            setattr(profile, k, v)
        profile.save()
        return user
    
    def tearDown(self):
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
        self.client.logout()
        super(LoginTestCase, self).tearDown()
