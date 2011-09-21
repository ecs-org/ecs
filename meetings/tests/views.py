import datetime
from django.core.urlresolvers import reverse
from urlparse import urlsplit
from ecs.utils.testcases import EcsTestCase
from ecs.meetings.models import Meeting
from ecs.core.tests.submissions import create_submission_form

def _get_datetime_inputs(name, dt):
    return {
        '%s_0' % name: dt.strftime('%d.%m.%Y'),
        '%s_1' % name: dt.strftime("%H:%M"),
    }

class ViewTestCase(EcsTestCase):
    '''Tests for timetable and meetingassistant.
    
    Tests for Timetable calculations and storage,
    consistency of the meetingassistant's actions when starting and stopping meetings,
    quickjump feature. 
    '''
    
    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.start = datetime.datetime(2020, 2, 20, 20, 20)
        self.user = self.create_user('unittest-internal', profile_extra={'internal': True})
        self.client.login(email='unittest-internal@example.com', password='password')

    def tearDown(self):
        super(ViewTestCase, self).tearDown()
        self.client.logout()

    def refetch(self, obj):
        return obj.__class__.objects.get(pk=obj.pk)

    def test_timetable(self):
        '''Tests if timetable durations are correct,
        and if meeting entries are correctly stored in the timetable.
        '''
        
        create_meeting_url = reverse('ecs.meetings.views.create_meeting')
        response = self.client.get(create_meeting_url)
        self.failUnlessEqual(response.status_code, 200)

        data = {}
        data.update(_get_datetime_inputs('start', self.start))
        data.update(_get_datetime_inputs('deadline_diplomathesis', self.start + datetime.timedelta(days=30)))
        data.update(_get_datetime_inputs('deadline', self.start + datetime.timedelta(days=14)))
        response = self.client.post(create_meeting_url, data)
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(Meeting.objects.filter(start=self.start).count(), 1)
        meeting = Meeting.objects.get(start=self.start)
        
        timetable_url = reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk})
        response = self.client.get(timetable_url)
        self.failUnlessEqual(response.status_code, 200)
        
        e0 = meeting.add_entry(duration_in_seconds=42)
        response = self.client.post(reverse('ecs.meetings.views.update_timetable_entry', kwargs={'meeting_pk': meeting.pk, 'entry_pk': e0.pk}), {
            'duration': '2h',
        })
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(self.refetch(e0).duration, datetime.timedelta(hours=2))
        
        e1 = meeting.add_entry(duration_in_seconds=42)
        self.failUnlessEqual(list(meeting), [e0, e1])
        
        response = self.client.get(reverse('ecs.meetings.views.move_timetable_entry', kwargs={'meeting_pk': meeting.pk}) + '?from_index=0&to_index=1')
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(list(self.refetch(meeting)), [e1, e0])
        
        response = self.client.get(reverse('ecs.meetings.views.remove_timetable_entry', kwargs={'meeting_pk': meeting.pk, 'entry_pk': e0.pk}))
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(list(self.refetch(meeting)), [e1])
        

    def test_meeting_assistant(self):
        '''Makes sure that the meeting assistant is fully functional.
        Tests that the meeting assistant starts and stops meetings correctly.
        '''
        
        meeting = Meeting.objects.create(start=self.start)
        submission = create_submission_form().submission
        e0 = meeting.add_entry(duration_in_seconds=42, submission=submission)
        e1 = meeting.add_entry(duration_in_seconds=42*42)

        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant_start', kwargs={'meeting_pk': meeting.pk}))
        self.failUnlessEqual(response.status_code, 302)
        meeting = self.refetch(meeting)
        self.failUnless(meeting.started)
        
        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))
        self.failUnlessEqual(response.status_code, 302)
        
        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': e0.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.post(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': e0.pk}), {
            'close_top': 'on',
            'result': '1',
        })
        self.failUnless(response.status_code, 302)
        self.failIf(self.refetch(e0).is_open)

        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant_stop', kwargs={'meeting_pk': meeting.pk}))
        self.failUnlessEqual(response.status_code, 404)

        response = self.client.post(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': e1.pk}), {
            'close_top': 'on',
            'result': '2',
        })
        self.failUnless(response.status_code, 302)
        self.failIf(self.refetch(e1).is_open)
        
        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant_stop', kwargs={'meeting_pk': meeting.pk}))
        self.failUnlessEqual(response.status_code, 302)
        meeting = self.refetch(meeting)
        self.failUnless(meeting.ended)

    def test_meeting_assistant_quickjump(self):
        '''Tests that the quickjump view is accessible and that it returns the right url.
        '''
        
        meeting = Meeting.objects.create(start=self.start, started=self.start)
        e0 = meeting.add_entry(duration_in_seconds=42)
        e1 = meeting.add_entry(duration_in_seconds=42*42)
        
        quickjump_url = reverse('ecs.meetings.views.meeting_assistant_quickjump', kwargs={'meeting_pk': meeting.pk})
        response = self.client.get(quickjump_url + '?q=')
        self.failUnless(response.status_code, 200)
        
        response = self.client.get(quickjump_url + '?q=TOP 1')
        self.failUnless(response.status_code, 302)
        self.failUnlessEqual(urlsplit(response['Location']).path, reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': e0.pk}))

