import re

from django.core.urlresolvers import reverse
from django.test.client import Client

from ecs.ecsmail.testcases import MailTestCase
from ecs.workflow.tests import WorkflowTestCase
from ecs.utils.testcases import EcsTestCase
from ecs.users.utils import get_user, create_user


class RegistrationTest(MailTestCase, WorkflowTestCase):
    '''Tests for the user registration functionality
    
    High level tests for the user registration. 
    '''
    
    def test_registration(self):
        '''Tests the registration process by registering as a new user,
        following the link in the registration mail message,
        setting a password and comparing the provided user data afterwards.
        '''
        
        from ecs.core.bootstrap import auth_groups
        from ecs.users.bootstrap import user_workflow

        # create user workflow
        auth_groups()
        user_workflow()

        response = self.client.post(reverse('ecs.users.views.register'), {
            'gender': 'm',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new.user@example.org',
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(self.queue_count(),1)
        mimetype, message = self.get_mimeparts(self.convert_raw2message(self.queue_get(0)), "text", "html") [0]
        
        # XXX: how do we get the right url without knowing its path-prefix? (FMD1)
        match = re.search(r'href="https?://[\w.]+(/activate/[^"]+)"', message)
        self.failUnless(match)
        activation_url = match.group(1)
        response = self.client.get(activation_url)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(activation_url, {
            'password': 'password',
            'password_again': 'password',
        })
        self.failUnlessEqual(response.status_code, 200)
        user = get_user('new.user@example.org')
        self.failUnlessEqual(user.first_name, 'New')
        self.failUnlessEqual(user.get_profile().gender, 'm')
        self.failUnless(user.check_password('password'))
        

class PasswordChangeTest(MailTestCase):
    '''Tests for password changing functionality
    
    High level tests for password changing and password reset functionality.
    '''
    
    def test_password_reset(self):
        '''Makes sure that a user can reset his password,
        by following the link in a password reset mail message,
        setting a new password and performing a test login with the newly set password.
        '''
        
        user = create_user('new.user@example.org')
        user.set_password('password')
        user.save()
        response = self.client.post(reverse('ecs.users.views.request_password_reset'), {
            'email': 'new.user@example.org',
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(self.queue_count(), 1)
        mimetype, message = self.get_mimeparts(self.convert_raw2message(self.queue_get(0)), "text", "html") [0]
        
        # XXX: how do we get the right url without knowing its path-prefix? (FMD1)
        match = re.search(r'href="https?://[^/]+(/password-reset/[^"]+)"', message)
        self.failUnless(match)
        password_reset_url = match.group(1)
        response = self.client.get(password_reset_url)
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.post(password_reset_url, {
            'new_password1': '1234',
            'new_password2': '1234',
        })
        self.failUnlessEqual(response.status_code, 200)
        user = get_user('new.user@example.org')
        self.failUnless(user.check_password('1234'))
        
        response = self.client.get(password_reset_url)
        self.failUnlessEqual(response.status_code, 200)
        self.failIf('form' in response.context)
        
    def test_password_change(self):
        '''Makes sure that a password can be changed, by changing a password and
        performing a test-login afterwards with the changed password.
        '''
        
        user = create_user('foobar@example.com')
        user.set_password('test')
        user.save()
        self.client.login(email='foobar@example.com', password='test')

        url = reverse('ecs.users.views.change_password')
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(url, {
            'old_password': 'test', 
            'new_password1': '1234',
            'new_password2': '1234',
        })
        self.failUnlessEqual(response.status_code, 200)
        self.client.logout()
        
        user = get_user('foobar@example.com')
        self.failUnless(user.check_password('1234'))
        
class MiddlewareTest(EcsTestCase):
    '''Tests for the user middleware
    
    High level tests for user middleware features such as single-login enforcement.
    '''
    
    def setUp(self, *args, **kwargs):
        testuser = create_user('testuser@example.com')
        testuser.set_password('4223')
        testuser.save()

        return super(MiddlewareTest, self).setUp(*args, **kwargs)

    def test_single_login(self):
        '''makes sure that a single user can only be logged in
        with one single client at any given time.
        '''
        c1 = Client()
        c2 = Client()

        c1.login(email='testuser@example.com', password='4223')
        response = c1.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.failUnlessEqual(response.status_code, 200)

        c2.login(email='testuser@example.com', password='4223')  # now, c1 has to be logged out, because of the single login middleware
        response = c2.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.failUnlessEqual(response.status_code, 200)

        response = c1.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.failUnlessEqual(response.status_code, 302)
        
