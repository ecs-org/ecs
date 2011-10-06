from django.db import models
from django.contrib.contenttypes.models import ContentType

from ecs.workflow.tests.base import WorkflowTestCase
from ecs.workflow.models import Graph, Node
from ecs.workflow.exceptions import TokenRequired, BadActivity, WorkflowError
from ecs import workflow
# test only models:
from ecs.workflow.models import Foo, FooReview, Token

from ecs.workflow.tests import flow_declarations as decl

class FlowTest(WorkflowTestCase):
    '''Tests for the workflow module
    
    Tests if the traversal of the workflow nodes works correctly.
    '''
    
    def setUp(self):
        super(FlowTest, self).setUp()
        self.foo_ct = ContentType.objects.get_for_model(Foo)
        
    def test_sequence(self):
        '''Tests if traversing workflow nodes in sequence works correctly.'''

        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True)
        n_b = g.create_node(decl.B)
        n_c = g.create_node(decl.C, end=True)
        n_a.add_edge(n_b)
        n_b.add_edge(n_c)
        
        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [decl.A])
        obj.workflow.do(decl.A)
        self.assertActivitiesEqual(obj, [decl.B])
        obj.workflow.do(decl.B)
        self.assertActivitiesEqual(obj, [decl.C])
        obj.workflow.do(decl.C)
        self.assertActivitiesEqual(obj, [])

    def test_parallel_split(self):
        '''Tests if branch split in the workflow is performed correctly.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True)
        n_b = g.create_node(decl.B)
        n_c = g.create_node(decl.C)
        n_a.add_edge(n_b)
        n_a.add_edge(n_c)
        
        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [decl.A])
        obj.workflow.do(decl.A)
        
        self.assertActivitiesEqual(obj, [decl.B, decl.C])
        obj.workflow.do(decl.B)
        
        self.assertActivitiesEqual(obj, [decl.C])
        obj.workflow.do(decl.C)
        
        self.assertActivitiesEqual(obj, [])
        
        # a, c, b
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [decl.A])
        obj.workflow.do(decl.A)
        
        self.assertActivitiesEqual(obj, [decl.B, decl.C])
        obj.workflow.do(decl.C)
        
        self.assertActivitiesEqual(obj, [decl.B])
        obj.workflow.do(decl.B)
        
    def test_simple_merge(self):
        '''Tests if a branch merge in the workflow graph is traversed correctly.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True)
        n_b = g.create_node(decl.B, start=True)
        n_c = g.create_node(decl.C)
        n_a.add_edge(n_c)
        n_b.add_edge(n_c)
        
        # a, c, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [decl.A, decl.B])
        obj.workflow.do(decl.A)

        self.assertActivitiesEqual(obj, [decl.B, decl.C])
        obj.workflow.do(decl.C)

        self.assertActivitiesEqual(obj, [decl.B])
        obj.workflow.do(decl.B)

        self.assertActivitiesEqual(obj, [decl.C])
        obj.workflow.do(decl.C)
        
        self.assertActivitiesEqual(obj, [])
        
        # a, b, c, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [decl.A, decl.B])
        obj.workflow.do(decl.A)

        self.assertActivitiesEqual(obj, [decl.B, decl.C])
        obj.workflow.do(decl.B)

        self.assertActivitiesEqual(obj, [decl.C, decl.C])
        obj.workflow.do(decl.C)

        self.assertActivitiesEqual(obj, [decl.C])
        obj.workflow.do(decl.C)
        
        self.assertActivitiesEqual(obj, [])
        
    def test_branching(self):
        '''Tests if conditional branch splits are being traversed as expected.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True)
        n_b = g.create_node(decl.B)
        n_c = g.create_node(decl.C)
        n_a.add_edge(n_b, guard=decl.GUARD)
        n_a.add_edge(n_c, guard=decl.GUARD, negated=True)
        
        # GUARD => False
        obj = Foo.objects.create(flag=False)
        
        self.assertActivitiesEqual(obj, [decl.A])
        obj.workflow.do(decl.A)
        
        self.assertActivitiesEqual(obj, [decl.C])
        obj.workflow.do(decl.C)

        self.assertActivitiesEqual(obj, [])
        
        # GUARD => True
        obj = Foo.objects.create(flag=True)
        
        self.assertActivitiesEqual(obj, [decl.A])
        obj.workflow.do(decl.A)
        
        self.assertActivitiesEqual(obj, [decl.B])
        obj.workflow.do(decl.B)

        self.assertActivitiesEqual(obj, [])
        
        
    def test_generic_control(self):
        '''Tests if the generic workflow node is implemented correctly.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_x0 = g.create_node(workflow.patterns.Generic, start=True)
        n_a = g.create_node(decl.A)
        n_x1 = g.create_node(workflow.patterns.Generic)
        n_b = g.create_node(decl.B)
        n_x2 = g.create_node(workflow.patterns.Generic)
        n_x3 = g.create_node(workflow.patterns.Generic, end=True)
        
        n_x0.add_edge(n_a)
        n_a.add_edge(n_x1)
        n_x1.add_edge(n_b)
        n_b.add_edge(n_x2)
        n_x2.add_edge(n_x3)
        
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [decl.A])
        obj.workflow.do(decl.A)

        self.assertActivitiesEqual(obj, [decl.B])
        obj.workflow.do(decl.B)

        self.assertActivitiesEqual(obj, [])

        
    def test_synchronization(self):
        '''Tests if a synchronized branch merge is performed correctly.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True)
        n_b = g.create_node(decl.B, start=True)
        n_sync = g.create_node(workflow.patterns.Synchronization)
        n_c = g.create_node(decl.C, end=True)
        n_a.add_edge(n_sync)
        n_b.add_edge(n_sync)
        n_sync.add_edge(n_c)

        # a, b, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [decl.A, decl.B])
        obj.workflow.do(decl.A)
        
        self.assertActivitiesEqual(obj, [decl.B])
        obj.workflow.do(decl.B)
        
        self.assertActivitiesEqual(obj, [decl.C])
        obj.workflow.do(decl.C)
        
        self.assertActivitiesEqual(obj, [])
        
        # b, a, c
        obj = Foo.objects.create()
        
        self.assertActivitiesEqual(obj, [decl.A, decl.B])
        obj.workflow.do(decl.B)
        
        self.assertActivitiesEqual(obj, [decl.A])
        obj.workflow.do(decl.A)
        
        self.assertActivitiesEqual(obj, [decl.C])
        obj.workflow.do(decl.C)
        
        self.assertActivitiesEqual(obj, [])
        
        
    def test_locks(self):
        '''Tests that the locking mechanisms for workflow nodes that require a token is implemented correctly.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_d = g.create_node(decl.D, start=True)
        n_b = g.create_node(decl.B)
        n_d.add_edge(n_b)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [decl.D])
        self.assertRaises(TokenRequired, obj.workflow.do, decl.D)
        
        decl.foo_change.send(obj)
        self.assertActivitiesEqual(obj, [decl.D])

        self.assertRaises(TokenRequired, obj.workflow.do, decl.D)
        self.assertActivitiesEqual(obj, [decl.D])

        obj.flag = True
        obj.save()
        self.assertActivitiesEqual(obj, [decl.D])

        self.assertRaises(TokenRequired, obj.workflow.do, decl.D)
        self.assertActivitiesEqual(obj, [decl.D])
        
        decl.foo_change.send(obj)
        self.assertActivitiesEqual(obj, [decl.D])

        obj.workflow.do(decl.D)
        self.assertActivitiesEqual(obj, [decl.B])
        
    def test_flow_controller_locks(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_f = g.create_node(decl.F, start=True)
        n_a = g.create_node(decl.A)
        n_f.add_edge(n_a)

        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [])
        
        decl.foo_change.send(obj)
        self.assertActivitiesEqual(obj, [])
        
        obj.flag = True
        obj.save()
        decl.foo_change.send(obj)
        self.assertActivitiesEqual(obj, [decl.A])

    def test_subgraph(self):
        '''Tests if the subgraph mechanism is implemented correctly.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        h = Graph.objects.create(name='TestSubGraph', content_type=self.foo_ct)
        n_b = h.create_node(decl.B, start=True)
        n_c = h.create_node(decl.C, end=True)
        n_b.add_edge(n_c)
        
        n_a = g.create_node(decl.A, start=True)
        n_h = g.create_node(h)
        n_e = g.create_node(decl.E, end=True)
        
        n_a.add_edge(n_h)
        n_h.add_edge(n_e)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [decl.A])
        
        obj.workflow.do(decl.A)
        self.assertActivitiesEqual(obj, [decl.B])

        obj.workflow.do(decl.B)
        self.assertActivitiesEqual(obj, [decl.C])

        obj.workflow.do(decl.C)
        self.assertActivitiesEqual(obj, [decl.E])

        obj.workflow.do(decl.E)
        self.assertActivitiesEqual(obj, [])
        
    def test_trail(self):
        '''Tests if the trail of a workflow token is recorded correctly'''

        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True)
        n_b = g.create_node(decl.B)
        n_c = g.create_node(decl.C)
        n_e = g.create_node(decl.E, end=True)
        n_sync = g.create_node(workflow.patterns.Synchronization)
        n_a.add_edge(n_b)
        n_a.add_edge(n_c)
        n_b.add_edge(n_sync)
        n_c.add_edge(n_sync)
        n_sync.add_edge(n_e)
        
        obj = Foo.objects.create()        
        obj.workflow.do(decl.A)
        
        obj.workflow.do(decl.B)
        obj.workflow.do(decl.C)
        obj.workflow.do(decl.E)

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
        '''Tests if parametrization of a workflow node is implemented correctly.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        
        r0 = FooReview.objects.create(name='R0')
        r1 = FooReview.objects.create(name='R1')
        n_v0 = g.create_node(decl.V, data=r0, start=True)
        n_v1 = g.create_node(decl.V, data=r1, end=True)        
        n_v0.add_edge(n_v1)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [decl.V])

        self.assertRaises(WorkflowError, obj.workflow.do, decl.V)
        self.assertRaises(WorkflowError, obj.workflow.do, decl.V, data=r1)
        obj.workflow.do(decl.V, data=r0)
        self.assertActivitiesEqual(obj, [decl.V])

        self.assertRaises(WorkflowError, obj.workflow.do, decl.V, data=r0)
        obj.workflow.do(decl.V, data=r1)
        self.assertActivitiesEqual(obj, [])
        
    def test_disable_autostart(self):
        '''Tests if disabling the workflow autostart behaves as expected.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True)
        
        obj = Foo.objects.create()
        self.assertActivitiesEqual(obj, [decl.A])
        
        with workflow.autostart_disabled():
            obj = Foo.objects.create()
            self.assertActivitiesEqual(obj, [])
        
        self.assertActivitiesEqual(obj, [])
