from datetime import timedelta
from django.db import models
from django.contrib.contenttypes.models import ContentType

from ecs.workflow.tests.base import WorkflowTestCase
from ecs.workflow.models import Graph, Node, NodeType, Guard
from ecs.workflow.exceptions import WorkflowError
# test only models:
from ecs.workflow.models import Foo

from ecs.workflow.tests import repeatability_declarations as decl

class RepeatabilityTest(WorkflowTestCase):
    '''Workflow repetition tests.'''
    
    def setUp(self):
        super(RepeatabilityTest, self).setUp()
        self.foo_ct = ContentType.objects.get_for_model(Foo)
        
    def test_unrepeatable(self):
        '''Tests that a certain task cannot be done again in the workflow.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True)
        n_c = g.create_node(decl.C, end=True)
        n_a.add_edge(n_c)

        obj = Foo.objects.create()
        obj.workflow.do(decl.A)
        self.assertRaises(WorkflowError, obj.workflow.do, decl.A)
        
        
    def test_simple_repeat(self):
        '''Tests that certain Tasks can be repeated in the workflow.'''
        
        g = Graph.objects.create(name='TestGraph', content_type=self.foo_ct, auto_start=True)
        n_a = g.create_node(decl.A, start=True) 
        n_b = g.create_node(decl.B) # repeatable
        n_c = g.create_node(decl.C) 
        n_d = g.create_node(decl.D) # not reentrant
        n_e = g.create_node(decl.E, end=True)
        n_a.add_edge(n_b)
        n_b.add_edge(n_c)
        n_c.add_edge(n_d)
        n_d.add_edge(n_e)
        
        obj = Foo.objects.create()
        
        self.assertRaises(WorkflowError, obj.workflow.do, decl.B)
        
        self.assertActivitiesEqual(obj, [decl.A])
        obj.workflow.do(decl.A)
        obj.workflow.do(decl.B)
        obj.workflow.do(decl.C)
        self.assertActivitiesEqual(obj, [decl.D])
        obj.workflow.do(decl.B)
        self.assertActivitiesEqual(obj, [decl.C, decl.D])
        obj.workflow.do(decl.C)
        self.assertActivitiesEqual(obj, [decl.D])
        obj.workflow.do(decl.B)
        obj.workflow.do(decl.D)
        self.assertActivitiesEqual(obj, [decl.C, decl.E])
        obj.workflow.do(decl.C)
        self.assertActivitiesEqual(obj, [decl.E])
        
        

