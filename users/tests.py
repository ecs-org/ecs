import re

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test.client import Client

from ecs.ecsmail.testcases import MailTestCase
from ecs.utils.testcases import EcsTestCase


class RegistrationTest(MailTestCase):
    def test_registration(self):
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
            'username': 'new.user@example.org',
            'password': 'password',
            'password_again': 'password',
        })
        self.failUnlessEqual(response.status_code, 200)
        user = User.objects.get(username='new.user@example.org')
        self.failUnlessEqual(user.first_name, 'New')
        self.failUnlessEqual(user.get_profile().gender, 'm')
        self.failUnless(user.check_password('password'))
        

class PasswordChangeTest(MailTestCase):
    def test_password_reset(self):
        user = User(username='new.user@example.org', email='new.user@example.org')
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
        user = User.objects.get(username='new.user@example.org')
        self.failUnless(user.check_password('1234'))
        
        response = self.client.get(password_reset_url)
        self.failUnlessEqual(response.status_code, 200)
        self.failIf('form' in response.context)
        
    def test_password_change(self):
        user = User(username='foobar')
        user.set_password('test')
        user.save()
        self.client.login(username='foobar', password='test')

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
        
        user = User.objects.get(username='foobar')
        self.failUnless(user.check_password('1234'))
        
class MiddlewareTest(EcsTestCase):
    def setUp(self, *args, **kwargs):
        testuser = User.objects.create(username='testuser')
        testuser.set_password('4223')
        testuser.save()

        return super(MiddlewareTest, self).setUp(*args, **kwargs)

    def test_single_login(self):
        c1 = Client()
        c2 = Client()

        c1.login(username='testuser', password='4223')
        response = c1.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.failUnlessEqual(response.status_code, 200)

        c2.login(username='testuser', password='4223')  # now, c1 has to be logged out, because of the single login middleware
        response = c2.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.failUnlessEqual(response.status_code, 200)

        response = c1.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.failUnlessEqual(response.status_code, 302)
        
