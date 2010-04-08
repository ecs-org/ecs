from datetime import datetime, timedelta, time
from django.test import TestCase

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



