import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from ecs.utils.testcases import EcsTestCase
from ecs.core.tests.submissions import create_submission_form
from ecs.core.models import Submission
from ecs.meetings.models import Meeting
from ecs.users.utils import sudo

class SubmissionAuthTestCase(EcsTestCase):
    def _create_test_user(self, name, **profile_attrs):
        user = User.objects.create(username=name)
        profile = user.get_profile()
        for name, value in profile_attrs.items():
            setattr(profile, name, value)
        profile.save()
        return user
    
    def setUp(self):
        super(SubmissionAuthTestCase, self).setUp()
        self.additional_review_user = self._create_test_user('additional_review', approved_by_office=True)
        self.anyone = self._create_test_user('anyone', approved_by_office=True)
        self.board_member_user = self._create_test_user('board_member', approved_by_office=True, board_member=True)
        self.expedited_review_user = self._create_test_user('expedited_review', approved_by_office=True, expedited_review=True)
        self.external_review_user = self._create_test_user('external_review', approved_by_office=True, external_review=True)
        self.insurance_review_user = self._create_test_user('insurance_review', approved_by_office=True, insurance_review=True)
        self.internal_user = self._create_test_user('internal', approved_by_office=True, internal=True)
        self.primary_investigator_user = self._create_test_user('primary_investigator', approved_by_office=True)
        self.sponsor_user = self._create_test_user('sponsor', approved_by_office=True)
        self.submitter_user = self._create_test_user('submitter', approved_by_office=True)
        self.thesis_review_user = self._create_test_user('thesis_review', approved_by_office=True, thesis_review=True)
        
        self.another_board_member_user = self._create_test_user('another_board_member', approved_by_office=True, board_member=True)
        self.unapproved_user = self._create_test_user('unapproved_user')
    
    def test_submission_auth(self):
        sf = create_submission_form()
        sf.submitter = self.submitter_user
        sf.sponsor = self.sponsor_user
        sf.additional_review_user = self.additional_review_user
        sf.save()
        investigator = sf.investigators.all()[0]
        investigator.user = self.primary_investigator_user
        investigator.save()

        sf.submission.additional_reviewers.add(self.additional_review_user)
        sf.submission.external_reviewer_name = self.external_review_user

        meeting = Meeting.objects.create(start=datetime.datetime.now())
        entry = meeting.add_entry(submission=sf.submission, duration_in_seconds=60)
        entry.add_user(self.board_member_user)
        sf.submission.next_meeting = meeting

        sf.submission.save()
        
        with sudo(self.unapproved_user):
            self.failUnlessEqual(Submission.objects.count(), 0)
        with sudo(self.anyone):
            self.failUnlessEqual(Submission.objects.count(), 0)
        with sudo(self.submitter_user):
            self.failUnlessEqual(Submission.objects.count(), 1)
        with sudo(self.sponsor_user):
            self.failUnlessEqual(Submission.objects.count(), 1)
        with sudo(self.primary_investigator_user):
            self.failUnlessEqual(Submission.objects.count(), 1)
        with sudo(self.additional_review_user):
            self.failUnlessEqual(Submission.objects.count(), 1)
        with sudo(self.internal_user):
            self.failUnlessEqual(Submission.objects.count(), 1)
        with sudo(self.external_review_user):
            self.failUnlessEqual(Submission.objects.count(), 1)
        with sudo(self.board_member_user):
            self.failUnlessEqual(Submission.objects.count(), 1)
        with sudo(self.another_board_member_user):
            self.failUnlessEqual(Submission.objects.count(), 0)

        with sudo(self.thesis_review_user):
            self.failUnlessEqual(Submission.objects.count(), 0)
        sf.submission.thesis = True
        sf.submission.save()
        with sudo(self.thesis_review_user):
            self.failUnlessEqual(Submission.objects.count(), 1)

        with sudo(self.expedited_review_user):
            self.failUnlessEqual(Submission.objects.count(), 0)
        sf.submission.expedited = True
        sf.submission.save()
        with sudo(self.thesis_review_user):
            self.failUnlessEqual(Submission.objects.count(), 1)

