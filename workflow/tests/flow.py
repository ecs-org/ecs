from django.test import TestCase
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core import management

from ecs.workflow.models import Graph, Node
from ecs.workflow.exceptions import TokenRequired
# test only models:
from ecs.workflow.models import Foo, FooReview, Token
from ecs import workflow

from ecs.workflow.tests import flow_declarations

class FlowTest(TestCase):
    def setUp(self):
        self.foo_ct = ContentType.objects.get_for_model(Foo)
        management.call_command('workflow_sync')
        
    def tearDown(self):
        workflow.clear_caches()
        
    def assertActivitiesEqual(self, obj, acts):
        self.failUnlessEqual(set(acts), set(bound_activity.activity for bound_activity in obj.workflow.activities))
        
    def test_sequence(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(flow_declarations.A, start=True)
        n_b = g.create_node(flow_declarations.B)
        n_c = g.create_node(flow_declarations.C, end=True)
        n_a.add_edge(n_b)
        n_b.add_edge(n_c)
        
        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A])
        bound_a = obj.workflow.get(flow_declarations.A)
        self.failUnlessEqual(flow_declarations.A, bound_a.activity)
        bound_a.perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.B])
        bound_b = obj.workflow.get(flow_declarations.B)
        self.failUnlessEqual(flow_declarations.B, bound_b.activity)
        bound_b.perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.C])
        bound_c = obj.workflow.get(flow_declarations.C)
        self.failUnlessEqual(flow_declarations.C, bound_c.activity)
        bound_c.perform()
        
        self.assertActivitiesEqual(obj, [])

    def test_parallel_split(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(flow_declarations.A, start=True)
        n_b = g.create_node(flow_declarations.B)
        n_c = g.create_node(flow_declarations.C)
        n_a.add_edge(n_b)
        n_a.add_edge(n_c)
        
        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A])
        obj.workflow.get(flow_declarations.A).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.B, flow_declarations.C])
        obj.workflow.get(flow_declarations.B).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()
        
        self.assertActivitiesEqual(obj, [])
        
        # a, c, b
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A])
        obj.workflow.get(flow_declarations.A).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.B, flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.B])
        obj.workflow.get(flow_declarations.B).perform()
        
    def test_simple_merge(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(flow_declarations.A, start=True)
        n_b = g.create_node(flow_declarations.B, start=True)
        n_c = g.create_node(flow_declarations.C)
        n_a.add_edge(n_c)
        n_b.add_edge(n_c)
        
        # a, c, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A, flow_declarations.B])
        obj.workflow.get(flow_declarations.A).perform()

        self.assertActivitiesEqual(obj, [flow_declarations.B, flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()

        self.assertActivitiesEqual(obj, [flow_declarations.B])
        obj.workflow.get(flow_declarations.B).perform()

        self.assertActivitiesEqual(obj, [flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()
        
        self.assertActivitiesEqual(obj, [])
        
        # a, b, c, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A, flow_declarations.B])
        obj.workflow.get(flow_declarations.A).perform()

        self.assertActivitiesEqual(obj, [flow_declarations.B, flow_declarations.C])
        obj.workflow.get(flow_declarations.B).perform()

        self.assertActivitiesEqual(obj, [flow_declarations.C, flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()

        self.assertActivitiesEqual(obj, [flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()
        
        self.assertActivitiesEqual(obj, [])
        
    def test_branching(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(flow_declarations.A, start=True)
        n_b = g.create_node(flow_declarations.B)
        n_c = g.create_node(flow_declarations.C)
        n_a.add_edge(n_b, guard=flow_declarations.GUARD)
        n_a.add_edge(n_c, guard=flow_declarations.GUARD, negate=True)
        
        # self.GUARD => False
        obj = Foo.objects.create(flag=False)
        
        self.assertActivitiesEqual(obj, [flow_declarations.A])
        obj.workflow.get(flow_declarations.A).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()

        self.assertActivitiesEqual(obj, [])
        
        # self.GUARD => True
        obj = Foo.objects.create(flag=True)
        
        self.assertActivitiesEqual(obj, [flow_declarations.A])
        obj.workflow.get(flow_declarations.A).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.B])
        obj.workflow.get(flow_declarations.B).perform()

        self.assertActivitiesEqual(obj, [])
        
        
    def test_generic_control(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_x0 = g.create_node(workflow.patterns.generic, start=True)
        n_a = g.create_node(flow_declarations.A)
        n_x1 = g.create_node(workflow.patterns.generic)
        n_b = g.create_node(flow_declarations.B)
        n_x2 = g.create_node(workflow.patterns.generic)
        n_x3 = g.create_node(workflow.patterns.generic, end=True)
        
        n_x0.add_edge(n_a)
        n_a.add_edge(n_x1)
        n_x1.add_edge(n_b)
        n_b.add_edge(n_x2)
        n_x2.add_edge(n_x3)
        
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A])
        obj.workflow.do(flow_declarations.A)

        self.assertActivitiesEqual(obj, [flow_declarations.B])
        obj.workflow.do(flow_declarations.B)

        self.assertActivitiesEqual(obj, [])

        
    def test_synchronization(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(flow_declarations.A, start=True)
        n_b = g.create_node(flow_declarations.B, start=True)
        n_sync = g.create_node(workflow.patterns.synchronization)
        n_c = g.create_node(flow_declarations.C, end=True)
        n_a.add_edge(n_sync)
        n_b.add_edge(n_sync)
        n_sync.add_edge(n_c)

        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A, flow_declarations.B])
        obj.workflow.get(flow_declarations.A).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.B])
        obj.workflow.get(flow_declarations.B).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()
        
        self.assertActivitiesEqual(obj, [])
        
        # b, a, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A, flow_declarations.B])
        obj.workflow.get(flow_declarations.B).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.A])
        obj.workflow.get(flow_declarations.A).perform()
        
        self.assertActivitiesEqual(obj, [flow_declarations.C])
        obj.workflow.get(flow_declarations.C).perform()
        
        self.assertActivitiesEqual(obj, [])
        
        
    def test_locks(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_d = g.create_node(flow_declarations.D, start=True)
        n_b = g.create_node(flow_declarations.B)
        n_d.add_edge(n_b)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [flow_declarations.D])
        self.assertRaises(TokenRequired, obj.workflow.do, flow_declarations.D)
        
        flow_declarations.foo_change.send(obj)
        self.assertActivitiesEqual(obj, [flow_declarations.D])

        self.assertRaises(TokenRequired, obj.workflow.do, flow_declarations.D)
        self.assertActivitiesEqual(obj, [flow_declarations.D])

        obj.flag = True
        obj.save()
        self.assertActivitiesEqual(obj, [flow_declarations.D])

        self.assertRaises(TokenRequired, obj.workflow.do, flow_declarations.D)
        self.assertActivitiesEqual(obj, [flow_declarations.D])
        
        flow_declarations.foo_change.send(obj)
        self.assertActivitiesEqual(obj, [flow_declarations.D])

        obj.workflow.do(flow_declarations.D)
        self.assertActivitiesEqual(obj, [flow_declarations.B])
        
    def test_subgraph(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        h = Graph.objects.create(name='TestSubGraph', content_type=self.foo_ct)
        n_b = h.create_node(flow_declarations.B, start=True)
        n_c = h.create_node(flow_declarations.C, end=True)
        n_b.add_edge(n_c)
        
        n_a = g.create_node(flow_declarations.A, start=True)
        n_h = g.create_node(h)
        n_e = g.create_node(flow_declarations.E, end=True)
        
        n_a.add_edge(n_h)
        n_h.add_edge(n_e)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [flow_declarations.A])
        
        obj.workflow.do(flow_declarations.A)
        self.assertActivitiesEqual(obj, [flow_declarations.B])

        obj.workflow.do(flow_declarations.B)
        self.assertActivitiesEqual(obj, [flow_declarations.C])

        obj.workflow.do(flow_declarations.C)
        self.assertActivitiesEqual(obj, [flow_declarations.E])

        obj.workflow.do(flow_declarations.E)
        self.assertActivitiesEqual(obj, [])
        
    def test_trail(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(flow_declarations.A, start=True)
        n_b = g.create_node(flow_declarations.B)
        n_c = g.create_node(flow_declarations.C)
        n_e = g.create_node(flow_declarations.E, end=True)
        n_sync = g.create_node(workflow.patterns.synchronization)
        n_a.add_edge(n_b)
        n_a.add_edge(n_c)
        n_b.add_edge(n_sync)
        n_c.add_edge(n_sync)
        n_sync.add_edge(n_e)
        
        obj = Foo.objects.create()        
        obj.workflow.do(flow_declarations.A)
        obj.workflow.do(flow_declarations.B)
        obj.workflow.do(flow_declarations.C)
        obj.workflow.do(flow_declarations.E)

        a_token = Token.objects.get(node=n_a)
        b_token = Token.objects.get(node=n_b)
        c_token = Token.objects.get(node=n_c)
        s_tokens = Token.objects.filter(node=n_sync)
        e_token = Token.objects.get(node=n_e)
        
        self.failUnlessEqual(set(a_token.trail.all()), set([]))
        self.failUnlessEqual(set(b_token.trail.all()), set([a_token]))
        self.failUnlessEqual(set(c_token.trail.all()), set([a_token]))
        self.failUnlessEqual(s_tokens.get(source=n_b).trail.get(), b_token)
        self.failUnlessEqual(s_tokens.get(source=n_c).trail.get(), c_token)
        self.failUnlessEqual(set(e_token.trail.all()), set(s_tokens))
        
        self.failUnlessEqual(a_token.activity_trail, set())
        self.failUnlessEqual(b_token.activity_trail, set([a_token]))
        self.failUnlessEqual(c_token.activity_trail, set([a_token]))
        self.failUnlessEqual(e_token.activity_trail, set([b_token, c_token]))

    def test_parametrization(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        
        r0 = FooReview.objects.create(name='R0')
        r1 = FooReview.objects.create(name='R1')
        n_v0 = g.create_node(flow_declarations.V, data=r0, start=True)
        n_v1 = g.create_node(flow_declarations.V, data=r1, end=True)        
        n_v0.add_edge(n_v1)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [flow_declarations.V])

        self.assertRaises(KeyError, obj.workflow.do, flow_declarations.V)
        self.assertRaises(KeyError, obj.workflow.do, flow_declarations.V, data=r1)
        obj.workflow.do(flow_declarations.V, data=r0)
        self.assertActivitiesEqual(obj, [flow_declarations.V])

        self.assertRaises(KeyError, obj.workflow.do, flow_declarations.V, data=r0)
        obj.workflow.do(flow_declarations.V, data=r1)
        self.assertActivitiesEqual(obj, [])
        
