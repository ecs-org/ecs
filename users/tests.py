import re
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from ecs.ecsmail.testcases import MailTestCase


class RegistrationTest(MailTestCase):
    def test_registration(self):
        response = self.client.post(reverse('ecs.users.views.register'), {
            'gender': 'm',
            'first_name': 'foo',
            'last_name': 'bar',
            'email': 'foobar@test.test',
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(self.queue_list()), 1)
        key, message = self.queue.pop()
        # FIXME: how do we get the right url without knowing its path-prefix?
        match = re.search(r'href="https?://[\w.]+(/activate/[^"]+)"', message.body())
        self.failUnless(match)
        activation_url = match.group(1)
        response = self.client.get(activation_url)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(activation_url, {
            'username': 'foobar',
            'password': 'test',
            'password_again': 'test',
        })
        self.failUnlessEqual(response.status_code, 200)
        user = User.objects.get(username='foobar')
        self.failUnlessEqual(user.first_name, 'foo')
        self.failUnlessEqual(user.get_profile().gender, 'm')
        self.failUnless(user.check_password('test'))
        

class PasswordChangeTest(MailTestCase):
    def test_password_reset(self):
        user = User(username='foobar', email='foobar@test.test')
        user.set_password('test')
        user.save()
        response = self.client.post(reverse('ecs.users.views.request_password_reset'), {
            'email': 'foobar@test.test',
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(self.queue_list()), 1)
        key, message = self.queue.pop()
        # FIXME: how do we get the right url without knowing its path-prefix?
        match = re.search(r'href="https?://[^/]+(/password-reset/[^"]+)"', message.body())
        self.failUnless(match)
        password_reset_url = match.group(1)
        response = self.client.get(password_reset_url)
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.post(password_reset_url, {
            'new_password1': '1234',
            'new_password2': '1234',
        })
        self.failUnlessEqual(response.status_code, 200)
        user = User.objects.get(username='foobar')
        self.failUnless(user.check_password('1234'))
        
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
        
        
