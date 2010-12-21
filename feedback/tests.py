"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse

from ecs.utils.testcases import EcsTestCase
from ecs.feedback.models import Feedback
from ecs.users.utils import create_user


class ViewTests(EcsTestCase):
    def setUp(self, *args, **kwargs):
        testuser = create_user('feedback@example.com')
        testuser.set_password('4223')
        testuser.save()
        super(ViewTests, self).setUp(*args, **kwargs)

    def test_feedback_input(self):
        response = self.client.post(reverse('ecs.feedback.views.feedback_input', kwargs={'type': 'q'}), {'description': 'Does it work?', 'fb_id': ''})
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(email='feedback@example.com', password='4223')
        response = self.client.post(reverse('ecs.feedback.views.feedback_input', kwargs={'type': 'q'}), {'description': 'Does it work?', 'fb_id': ''})
        self.failUnlessEqual(response.status_code, 200)


