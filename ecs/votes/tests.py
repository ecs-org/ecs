from datetime import timedelta

from django.utils import timezone

from ecs.communication.testcases import CommunicationTestCase
from ecs.core.tests.test_submissions import create_submission_form
from ecs.votes.tasks import send_reminder_messages
from ecs.votes.models import Vote
from ecs.core.models import AdvancedSettings


class VoteRemindersTest(CommunicationTestCase):
    '''Tests for reminder message sending and vote reminders
        Test that check if reminder messages get sent and if the reminder messages get delivered.
    '''

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        # alice is the submitter and bob is the default contact
        AdvancedSettings.objects.filter(pk=1).update(default_contact=self.bob)
        # there has to be a test submission
        submission_form = create_submission_form()
        submission_form.submitter_email = self.alice.email
        submission_form.save()
        self.submission_form = submission_form
        self.threads = submission_form.submission.thread_set
        self.vote = None
        self.now = timezone.now()

    def _create_B1_vote(self):
        self.vote = Vote.objects.create(submission_form=self.submission_form,
            result='1', published_at=self.now, valid_until=self.now + timedelta(days=365))

    def _create_B2_vote(self):
        self.vote = Vote.objects.create(submission_form=self.submission_form,
            result='2', published_at=self.now)

    def test_expiry(self):
        '''Tests that reminder messages actually get sent to submission participants.'''
        self._create_B1_vote()
        alice_threads = self.threads.filter(receiver=self.alice)
        bob_threads = self.threads.filter(receiver=self.bob)
        alice_thread_count = alice_threads.count()
        bob_thread_count = bob_threads.count()
        send_reminder_messages(
            today=self.vote.valid_until.date() + timedelta(days=1))
        self.assertEqual(alice_thread_count + 1, alice_threads.count())
        self.assertEqual(bob_thread_count + 1, bob_threads.count())

    def test_reminder_office(self):
        '''Tests that messages get sent to office before the deadline'''
        self._create_B1_vote()
        threads = self.threads.filter(receiver=self.bob)
        thread_count = threads.count()
        send_reminder_messages(
            today=self.vote.valid_until.date() - timedelta(days=7))
        self.assertEqual(thread_count + 1, threads.count())

    def test_reminder_submitter(self):
        '''Tests if the submitter of a study gets a reminder message.'''
        self._create_B1_vote()
        threads = self.threads.filter(receiver=self.alice)
        thread_count = threads.count()
        send_reminder_messages(
            today=self.vote.valid_until.date() - timedelta(days=21))
        self.assertEqual(thread_count + 1, threads.count())

    def test_temporary_reminder_submitter(self):
        '''Tests if the submitter is reminded of a temporary vote.'''
        self._create_B2_vote()
        threads = self.threads.filter(receiver=self.alice)
        thread_count = threads.count()
        send_reminder_messages(
            today=self.vote.published_at.date() + timedelta(days=183))
        self.assertEqual(thread_count + 1, threads.count())

    def test_temporary_reminder_office(self):
        '''Tests if the office is reminded of a temporary vote.'''
        self._create_B2_vote()
        threads = self.threads.filter(receiver=self.bob)
        thread_count = threads.count()
        send_reminder_messages(
            today=self.vote.published_at.date() + timedelta(days=365))
        self.assertEqual(thread_count + 1, threads.count())
