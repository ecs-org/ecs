# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.conf import settings
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
        submission_form.submission.save()
        submission_form.project_type_education_context = None
        submission_form.submitter_email = self.alice.email
        submission_form.save()

        submission_form_thesis = create_submission_form()
        submission_form_thesis.submission.is_thesis = True
        submission_form_thesis.submission.save()
        submission_form_thesis.project_type_education_context = 1  # "Dissertation"
        submission_form_thesis.submitter_email = self.alice.email
        submission_form_thesis.save()

        meeting = Meeting.objects.create(title='January Meeting', start=datetime(2042, 1, 1))
        meeting.started = meeting.start
        meeting.ended = meeting.start + timedelta(hours=8)
        meeting.deadline = meeting.start - timedelta(days=7)
        meeting.deadline_diplomathesis = meeting.start - timedelta(days=2)
        meeting.save()

        meeting.add_entry(submission=submission_form.submission, duration=timedelta(seconds=60))
        meeting.add_entry(submission=submission_form_thesis.submission, duration=timedelta(seconds=60))

        now = timezone.now()
        next_year = now + timedelta(days=365)
        self.valid_until = timezone.now().date() + timedelta(days=365)
        self.vote = Vote.objects.create(submission_form=submission_form, top=meeting.timetable_entries.get(submission=submission_form.submission), result='1', published_at=now, valid_until=next_year)
        self.vote_thesis = Vote.objects.create(submission_form=submission_form_thesis, top=meeting.timetable_entries.get(submission=submission_form_thesis.submission), result='1', published_at=now, valid_until=next_year)

    def test_expiry(self):
        '''Tests that reminder messages actually get sent to submission participants.
        '''
        
        alice_message_count = Message.objects.filter(receiver=self.alice).count()
        bob_message_count = Message.objects.filter(receiver=self.bob).count()
        send_reminder_messages(today=self.valid_until+timedelta(days=1))
        self.assertTrue(alice_message_count < Message.objects.filter(receiver=self.alice).count())
        self.assertTrue(bob_message_count < Message.objects.filter(receiver=self.bob).count())

    def test_expiry_diplomathesis(self):
        '''Tests that reminder messages actually get sent to submission participants in a diploma thesis submission.
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

    def test_reminder_office_diplomathesis(self):
        '''Tests that messages get sent to office for a thesis submission
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

    def test_reminder_submitter_diplomathesis(self):
        '''Tests if the submitter of a diploma thesis gets a reminder message.
        '''
        
        message_count = Message.objects.filter(receiver=self.alice).count()
        send_reminder_messages(today=self.valid_until-timedelta(days=21))
        self.assertTrue(message_count < Message.objects.filter(receiver=self.alice).count())

