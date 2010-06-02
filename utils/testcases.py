from django.test import TestCase

from django.contrib.auth.models import User

class LoginTestCase(TestCase):
    def setUp(self):
        user = User(username='unittest')
        user.set_password('password')
        user.save()
        self.client.login(username='unittest', password='password')
    
    def tearDown(self):
        self.client.logout()