from django.test import TestCase
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.dispatch import Signal
from django.db.models.signals import post_save
from django.core import management

from ecs.workflow.models import Graph, Node
from ecs.workflow.exceptions import TokenRequired
from ecs import workflow

class Foo(models.Model):
    flag = models.BooleanField(default=False)

    class Meta:
        app_label='workflow'

workflow.register(Foo)

foo_change = Signal()

a = workflow.declare_activity(Foo, 'do_A')
b = workflow.declare_activity(Foo, 'do_B')
c = workflow.declare_activity(Foo, 'do_C')
d = workflow.declare_activity(Foo, 'do_D', lock=lambda wf: wf.data.flag, signal=foo_change)
e = workflow.declare_activity(Foo, 'do_E')

def _flag_test(wf):
    return wf.data.flag

flag_test = workflow.declare_guard(Foo, 'flag_set', _flag_test)

class FlowTest(TestCase):
    def setUp(self):
        management.call_command('workflow_sync')
        self.foo_ct = ContentType.objects.get_for_model(Foo)
        
    def assertActivitiesEqual(self, obj, acts):
        self.failUnlessEqual(acts, [bound_activity.activity for bound_activity in obj.workflow.activities])
        
    def test_sequence(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(a, start=True)
        n_b = g.create_node(b)
        n_c = g.create_node(c, end=True)
        n_a.add_edge(n_b)
        n_b.add_edge(n_c)
        
        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [a])
        bound_a = obj.workflow.get(a)
        self.failUnlessEqual(a, bound_a.activity)
        bound_a.perform()
        
        self.assertActivitiesEqual(obj, [b])
        bound_b = obj.workflow.get(b)
        self.failUnlessEqual(b, bound_b.activity)
        bound_b.perform()
        
        self.assertActivitiesEqual(obj, [c])
        bound_c = obj.workflow.get(c)
        self.failUnlessEqual(c, bound_c.activity)
        bound_c.perform()
        
        self.assertActivitiesEqual(obj, [])

    def test_parallel_split(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(a, start=True)
        n_b = g.create_node(b)
        n_c = g.create_node(c)
        n_a.add_edge(n_b)
        n_a.add_edge(n_c)
        
        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [a])
        obj.workflow.get(a).perform()
        
        self.assertActivitiesEqual(obj, [b, c])
        obj.workflow.get(b).perform()
        
        self.assertActivitiesEqual(obj, [c])
        obj.workflow.get(c).perform()
        
        self.assertActivitiesEqual(obj, [])
        
        # a, c, b
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [a])
        obj.workflow.get(a).perform()
        
        self.assertActivitiesEqual(obj, [b, c])
        obj.workflow.get(c).perform()
        
        self.assertActivitiesEqual(obj, [b])
        obj.workflow.get(b).perform()
        
    def test_simple_merge(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(a, start=True)
        n_b = g.create_node(b, start=True)
        n_c = g.create_node(c)
        n_a.add_edge(n_c)
        n_b.add_edge(n_c)
        
        # a, c, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [a, b])
        obj.workflow.get(a).perform()

        self.assertActivitiesEqual(obj, [b, c])
        obj.workflow.get(c).perform()

        self.assertActivitiesEqual(obj, [b])
        obj.workflow.get(b).perform()

        self.assertActivitiesEqual(obj, [c])
        obj.workflow.get(c).perform()
        
        self.assertActivitiesEqual(obj, [])
        
        # a, b, c, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [a, b])
        obj.workflow.get(a).perform()

        self.assertActivitiesEqual(obj, [b, c])
        obj.workflow.get(b).perform()

        self.assertActivitiesEqual(obj, [c, c])
        obj.workflow.get(c).perform()

        self.assertActivitiesEqual(obj, [c])
        obj.workflow.get(c).perform()
        
        self.assertActivitiesEqual(obj, [])
        
    def test_branching(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(a, start=True)
        n_b = g.create_node(b)
        n_c = g.create_node(c)
        n_a.add_edge(n_b, guard=flag_test)
        n_a.add_edge(n_c, guard=flag_test, negate=True)
        
        # flag_test => False
        obj = Foo.objects.create(flag=False)
        
        self.assertActivitiesEqual(obj, [a])
        obj.workflow.get(a).perform()
        
        self.assertActivitiesEqual(obj, [c])
        obj.workflow.get(c).perform()

        self.assertActivitiesEqual(obj, [])
        
        # flag_test => True
        obj = Foo.objects.create(flag=True)
        
        self.assertActivitiesEqual(obj, [a])
        obj.workflow.get(a).perform()
        
        self.assertActivitiesEqual(obj, [b])
        obj.workflow.get(b).perform()

        self.assertActivitiesEqual(obj, [])
        
        #print g.dot
        
    def test_generic_control(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_x0 = g.create_node(workflow.controller.generic, start=True)
        n_a = g.create_node(a)
        n_x1 = g.create_node(workflow.controller.generic)
        n_b = g.create_node(b)
        n_x2 = g.create_node(workflow.controller.generic)
        n_x3 = g.create_node(workflow.controller.generic, end=True)
        
        n_x0.add_edge(n_a)
        n_a.add_edge(n_x1)
        n_x1.add_edge(n_b)
        n_b.add_edge(n_x2)
        n_x2.add_edge(n_x3)
        
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [a])
        obj.workflow.do(a)

        self.assertActivitiesEqual(obj, [b])
        obj.workflow.do(b)

        self.assertActivitiesEqual(obj, [])

        
    def test_synchronization(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(a, start=True)
        n_b = g.create_node(b, start=True)
        n_sync = g.create_node(workflow.controller.synchronization)
        n_c = g.create_node(c, end=True)
        n_a.add_edge(n_sync)
        n_b.add_edge(n_sync)
        n_sync.add_edge(n_c)

        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [a, b])
        obj.workflow.get(a).perform()
        
        self.assertActivitiesEqual(obj, [b])
        obj.workflow.get(b).perform()
        
        self.assertActivitiesEqual(obj, [c])
        obj.workflow.get(c).perform()
        
        self.assertActivitiesEqual(obj, [])
        
        # b, a, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [a, b])
        obj.workflow.get(b).perform()
        
        self.assertActivitiesEqual(obj, [a])
        obj.workflow.get(a).perform()
        
        self.assertActivitiesEqual(obj, [c])
        obj.workflow.get(c).perform()
        
        self.assertActivitiesEqual(obj, [])
        
        #print g.dot
        
    def test_locks(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_d = g.create_node(d, start=True)
        n_b = g.create_node(b)
        n_d.add_edge(n_b)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [d])
        self.assertRaises(TokenRequired, obj.workflow.do, d)
        
        foo_change.send(obj)
        self.assertActivitiesEqual(obj, [d])

        self.assertRaises(TokenRequired, obj.workflow.do, d)
        self.assertActivitiesEqual(obj, [d])

        obj.flag = True
        obj.save()
        self.assertActivitiesEqual(obj, [d])

        self.assertRaises(TokenRequired, obj.workflow.do, d)
        self.assertActivitiesEqual(obj, [d])
        
        foo_change.send(obj)
        self.assertActivitiesEqual(obj, [d])

        obj.workflow.do(d)
        self.assertActivitiesEqual(obj, [b])
        
    def test_subgraph(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        h = Graph.objects.create(name='TestSubGraph', content_type=self.foo_ct)
        n_b = h.create_node(b, start=True)
        n_c = h.create_node(c, end=True)
        n_b.add_edge(n_c)
        
        n_a = g.create_node(a, start=True)
        n_h = g.create_node(h)
        n_e = g.create_node(e, end=True)
        
        n_a.add_edge(n_h)
        n_h.add_edge(n_e)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [a])
        
        obj.workflow.do(a)
        self.assertActivitiesEqual(obj, [b])

        obj.workflow.do(b)
        self.assertActivitiesEqual(obj, [c])

        obj.workflow.do(c)
        self.assertActivitiesEqual(obj, [e])

        obj.workflow.do(e)
        self.assertActivitiesEqual(obj, [])
        

