"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from ecs.utils.testcases import EcsTestCase
from ecs.feedback.models import Feedback

class SimpleTest(EcsTestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

class ViewTests(EcsTestCase):
    def setUp(self, *args, **kwargs):
        testuser = User.objects.create(username='feedbackuser')
        testuser.set_password('4223')
        testuser.save()
        super(ViewTests, self).setUp(*args, **kwargs)

    def test_feedback_main(self):
        response = self.client.get(reverse('ecs.feedback.views.feedback_main'))
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(username='feedbackuser', password='4223')
        response = self.client.get(reverse('ecs.feedback.views.feedback_main'))
        self.failUnlessEqual(response.status_code, 200)

    def test_feedback_origins(self):
        response = self.client.get(reverse('ecs.feedback.views.feedback_origins'))
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(username='feedbackuser', password='4223')
        response = self.client.get(reverse('ecs.feedback.views.feedback_origins'))
        self.failUnlessEqual(response.status_code, 200)

    def test_feedback_input(self):
        response = self.client.post(reverse('ecs.feedback.views.feedback_input', kwargs={'type': 'q'}), {'description': 'Does it work?', 'fb_id': ''})
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(username='feedbackuser', password='4223')
        response = self.client.post(reverse('ecs.feedback.views.feedback_input', kwargs={'type': 'q'}), {'description': 'Does it work?', 'fb_id': ''})
        self.failUnlessEqual(response.status_code, 200)

    def test_mee_too(self):
        self.client.login(username='feedbackuser', password='4223')
        response = self.client.post(reverse('ecs.feedback.views.feedback_input', kwargs={'type': 'i'}), {'description': 'Lets test the mee too feature', 'fb_id': ''})
        self.failUnlessEqual(response.status_code, 200)
        self.client.logout()

        fb_id = Feedback.objects.all()[0].id
        response = self.client.post(reverse('ecs.feedback.views.feedback_input', kwargs={'type': 'i'}), {'description': 'Me likes it too', 'fb_id': fb_id})
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(username='feedbackuser', password='4223')
        response = self.client.post(reverse('ecs.feedback.views.feedback_input', kwargs={'type': 'i'}), {'description': 'Me likes it too', 'fb_id': fb_id})
        self.failUnlessEqual(response.status_code, 200)

    def test_feedback_details(self):
        self.client.login(username='feedbackuser', password='4223')
        response = self.client.post(reverse('ecs.feedback.views.feedback_input', kwargs={'type': 'i'}), {'description': 'Lets test the mee too feature', 'fb_id': ''})
        self.failUnlessEqual(response.status_code, 200)
        self.client.logout()

        fb_id = Feedback.objects.all()[0].id
        response = self.client.get(reverse('ecs.feedback.views.feedback_details', kwargs={'id': fb_id}))
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(username='feedbackuser', password='4223')
        response = self.client.get(reverse('ecs.feedback.views.feedback_details', kwargs={'id': fb_id}))
        self.failUnlessEqual(response.status_code, 200)

