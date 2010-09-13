import math
from datetime import datetime, timedelta, time
from django.test import TestCase
from django.db.models import connection
from django.contrib.auth.models import User

from ecs.core.models import Meeting

class MeetingModelTest(TestCase):
    def test_entry_management(self):
        start = datetime(2010, 4, 8, 0)
        m = Meeting.objects.create(start=start, title="Test")
        a = m.add_entry(duration=timedelta(minutes=30), title="A")
        b = m.add_entry(duration=timedelta(hours=1), title="B")
        c = m.add_entry(duration=timedelta(minutes=15), title="C")
        
        self.failUnlessEqual(len(m), 3)
        self.failUnlessEqual(list(m), [a, b, c])
        a.index = 1
        self.failUnlessEqual(list(m), [b, a, c])
        a.index = 0
        self.failUnlessEqual(list(m), [a, b, c])

        self.assertRaises(IndexError, lambda: setattr(a, 'index', 3))
        self.assertRaises(IndexError, lambda: setattr(a, 'index', -1))
        
        self.failUnlessEqual(m[0], a)
        self.failUnlessEqual(m[2], c)
        self.assertRaises(IndexError, lambda: m[-1])
        self.assertRaises(IndexError, lambda: m[3])
        
        timetable = list(m)
        self.failUnlessEqual(timetable[0].start - start, timedelta(minutes=0))
        self.failUnlessEqual(timetable[0].end - start, timedelta(minutes=30))
        self.failUnlessEqual(timetable[1].start - start, timedelta(minutes=30))
        self.failUnlessEqual(timetable[1].end - start, timedelta(minutes=90))
        self.failUnlessEqual(timetable[2].start - start, timedelta(minutes=90))
        self.failUnlessEqual(timetable[2].end - start, timedelta(minutes=105))

        self.failUnlessEqual(m[0].start - start, timedelta(minutes=0))
        self.failUnlessEqual(m[0].end - start, timedelta(minutes=30))
        self.failUnlessEqual(m[1].start - start, timedelta(minutes=30))
        self.failUnlessEqual(m[1].end - start, timedelta(minutes=90))
        self.failUnlessEqual(m[2].start - start, timedelta(minutes=90))
        self.failUnlessEqual(m[2].end - start, timedelta(minutes=105))


    def test_metrics(self):
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
        query_count = len(connection.queries)

        wtpu = metrics.waiting_time_per_user
        self.failUnlessEqual(len(wtpu), 4)
        self.failUnlessEqual(wtpu[u0], timedelta(hours=4))
        self.failUnlessEqual(wtpu[u1], timedelta(hours=4))
        self.failUnlessEqual(wtpu[u2], timedelta(hours=0))
        self.failUnlessEqual(wtpu[u3], timedelta(hours=6))
        self.failUnlessEqual(metrics.waiting_time_total, timedelta(hours=14))
        self.failUnlessEqual(metrics.waiting_time_avg, timedelta(hours=3.5))
        self.failUnlessEqual(metrics.waiting_time_min, timedelta(hours=0))
        self.failUnlessEqual(metrics.waiting_time_max, timedelta(hours=6))
        self.failUnlessEqual(metrics.waiting_time_variance, timedelta(hours=math.sqrt(4.75)))
        
        self.failUnlessEqual(len(connection.queries), query_count)        
        


