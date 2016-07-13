from datetime import datetime, timedelta

import pytz

from django.utils import timezone

from ecs.communication.testcases import CommunicationTestCase
from ecs.core.tests.test_submissions import create_submission_form
from ecs.votes.tasks import send_reminder_messages
from ecs.meetings.models import Meeting
from ecs.votes.models import Vote
from ecs.communication.models import Message
from ecs.core.models import AdvancedSettings

class VoteRemindersTest(CommunicationTestCase):
    '''Tests for reminder message sending and vote reminders
    
    Test that check if reminder messages get sent and if the reminder messages get delivered.
    '''
    
    def setUp(self, *args, **kwargs):
        super(VoteRemindersTest, self).setUp(*args, **kwargs)

        # alice is the submitter and bob is the default contact
        advanced_settings = AdvancedSettings.objects.get(pk=1)
        advanced_settings.default_contact = self.bob
        advanced_settings.save()
        
        # there has to be a test submission
        submission_form = create_submission_form()
        submission_form.submitter_email = self.alice.email
        submission_form.save()

        now = timezone.now()
        next_year = now + timedelta(days=365)
        self.valid_until = timezone.now().date() + timedelta(days=365)
        self.vote = Vote.objects.create(submission_form=submission_form,
            result='1', published_at=now, valid_until=next_year)

    def test_expiry(self):
        '''Tests that reminder messages actually get sent to submission participants.
        '''
        
        alice_message_count = Message.objects.filter(receiver=self.alice).count()
        bob_message_count = Message.objects.filter(receiver=self.bob).count()
        send_reminder_messages(today=self.valid_until+timedelta(days=1))
        self.assertTrue(alice_message_count < Message.objects.filter(receiver=self.alice).count())
        self.assertTrue(bob_message_count < Message.objects.filter(receiver=self.bob).count())

    def test_reminder_office(self):
        '''Tests that messages get sent to office before the deadline
        '''
        
        message_count = Message.objects.filter(receiver=self.bob).count()
        send_reminder_messages(today=self.valid_until-timedelta(days=7))
        self.assertTrue(message_count < Message.objects.filter(receiver=self.bob).count())

    def test_reminder_submitter(self):
        '''Tests if the submitter of a study gets a reminder message.
        '''
        
        message_count = Message.objects.filter(receiver=self.alice).count()
        send_reminder_messages(today=self.valid_until-timedelta(days=21))
        self.assertTrue(message_count < Message.objects.filter(receiver=self.alice).count())
