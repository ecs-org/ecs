import math
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from ecs.utils.testcases import EcsTestCase
from ecs.meetings.models import Meeting
from ecs.core.tests.test_submissions import create_submission_form

class MeetingModelTest(EcsTestCase):
    '''Tests for the Meeting module
    
    Test for scheduling meetings, meeting entries (and the their order) and waiting time calculation and distribution. 
    '''
    
    def test_entry_management(self):
        '''Tests that entries can be added to a Meeting, that the order is correct
        and that start and end times of meeting items are correct.
        '''
        
        start = timezone.make_aware(
            datetime(2010, 4, 8, 0), timezone.get_current_timezone())
        m = Meeting.objects.create(start=start, title="Test")
        a = m.add_entry(duration=timedelta(minutes=30), title="A")
        b = m.add_entry(duration=timedelta(hours=1), title="B")
        c = m.add_entry(duration=timedelta(minutes=15), title="C")
        
        self.assertEqual(len(m), 3)
        self.assertEqual(list(m), [a, b, c])
        a.index = 1
        self.assertEqual(list(m), [b, a, c])
        a.index = 0
        self.assertEqual(list(m), [a, b, c])

        self.assertRaises(IndexError, lambda: setattr(a, 'index', 3))
        self.assertRaises(IndexError, lambda: setattr(a, 'index', -1))
        
        self.assertEqual(m[0], a)
        self.assertEqual(m[2], c)
        self.assertRaises(IndexError, lambda: m[-1])
        self.assertRaises(IndexError, lambda: m[3])
        
        timetable = list(m)
        self.assertEqual(timetable[0].start - start, timedelta(minutes=0))
        self.assertEqual(timetable[0].end - start, timedelta(minutes=30))
        self.assertEqual(timetable[1].start - start, timedelta(minutes=30))
        self.assertEqual(timetable[1].end - start, timedelta(minutes=90))
        self.assertEqual(timetable[2].start - start, timedelta(minutes=90))
        self.assertEqual(timetable[2].end - start, timedelta(minutes=105))

        self.assertEqual(m[0].start - start, timedelta(minutes=0))
        self.assertEqual(m[0].end - start, timedelta(minutes=30))
        self.assertEqual(m[1].start - start, timedelta(minutes=30))
        self.assertEqual(m[1].end - start, timedelta(minutes=90))
        self.assertEqual(m[2].start - start, timedelta(minutes=90))
        self.assertEqual(m[2].end - start, timedelta(minutes=105))


    def test_metrics(self):
        '''Tests that meeting items and their associated waiting times
        are evenly and correctly distributed among test users.
        '''
        
        u0, u1, u2, u3 = [User.objects.create(username='u%s' % i) for i in range(4)]
        
        start = datetime(2010, 4, 8, 0)
        m = Meeting.objects.create(start=start, title="Test")
        a = m.add_entry(duration=timedelta(hours=1), title="A")
        b = m.add_entry(duration=timedelta(hours=2), title="B")
        c = m.add_entry(duration=timedelta(hours=4), title="C")
        d = m.add_entry(duration=timedelta(hours=8), title="D")
        
        a.add_user(u0)
        a.add_user(u3)

        b.add_user(u0)
        b.add_user(u1)

        c.add_user(u2)

        d.add_user(u0)
        d.add_user(u1)
        d.add_user(u2)
        d.add_user(u3)
        
        metrics = m.metrics

        with self.assertNumQueries(0):
            wtpu = metrics.waiting_time_per_user
            self.assertEqual(len(wtpu), 4)
            self.assertEqual(wtpu[u0], timedelta(hours=4))
            self.assertEqual(wtpu[u1], timedelta(hours=4))
            self.assertEqual(wtpu[u2], timedelta(hours=0))
            self.assertEqual(wtpu[u3], timedelta(hours=6))
            self.assertEqual(metrics.waiting_time_total, timedelta(hours=14))
            self.assertEqual(metrics.waiting_time_avg, timedelta(hours=3.5))
            self.assertEqual(metrics.waiting_time_min, timedelta(hours=0))
            self.assertEqual(metrics.waiting_time_max, timedelta(hours=6))
            self.assertEqual(metrics.waiting_time_variance, timedelta(hours=math.sqrt(4.75)))
        
    def test_automatic_meeting_assignment(self):
        '''Tests the scheduling mechanism for meetings by scheduling
        and unscheduling meetings and then checking for the next meeting.
        '''
        
        s = create_submission_form().submission

        step = timedelta(days=1)
        start = timezone.now() + step
        meetings = [Meeting.objects.create(start=start + step * i, title="M%s" % i) for i in range(3)]

        def schedule(i):
            meetings[i].add_entry(submission=s, duration=timedelta(hours=1))
            
        def unschedule(i):
            meetings[i].timetable_entries.all().delete()
            
        def check_next(i):
            try:
                next_meeting = s.meetings.order_by('start')[0]
            except IndexError:
                next_meeting = None
            self.assertEqual(next_meeting, None if i is None else meetings[i])

        schedule(1)
        check_next(1)

        schedule(2)
        check_next(1)

        unschedule(1)
        check_next(2)

        unschedule(2)
        check_next(None)
        
        schedule(2)
        check_next(2)
        
        schedule(0)
        check_next(0)
        
        schedule(1)
        check_next(0)
        
        schedule(2)
        check_next(0)

        unschedule(0)
        check_next(1)
        

