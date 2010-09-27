from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core import management
from ecs.workflow.models import Graph
from ecs import workflow
# test only models:
from ecs.workflow.models import Foo
from ecs.workflow.tests import flow_declarations as decl
from ecs.workflow.tests import WorkflowTestCase

from ecs.utils.testcases import EcsTestCase
from ecs.tasks.models import Task, TaskType


class WorkflowIntegrationTest(WorkflowTestCase):
    def setUp(self):
        super(WorkflowIntegrationTest, self).setUp()
        self.foo_ct = ContentType.objects.get_for_model(Foo)

        g = Graph.objects.create(content_type=self.foo_ct, auto_start=True)
        self.n_a = g.create_node(decl.A, start=True)
        self.n_x = g.create_node(workflow.patterns.Generic)
        self.n_b = g.create_node(decl.B, end=True)
        self.n_a.add_edge(self.n_x)
        self.n_x.add_edge(self.n_b)
        self.graph = g
        
    def test_task_types(self):
        self.failUnless(TaskType.objects.get(workflow_node=self.n_a))
        self.failUnless(TaskType.objects.get(workflow_node=self.n_b))
        self.assertRaises(TaskType.DoesNotExist, TaskType.objects.get, workflow_node=self.n_x)
        
    def test_task_creation(self):
        obj = Foo.objects.create()
        
        tasks = Task.objects.for_data(obj).filter(closed_at=None)
        self.failUnlessEqual(tasks[0].task_type.workflow_node, self.n_a)
        self.assertRaises(Task.DoesNotExist, tasks.get, task_type__workflow_node=self.n_b)
        
        obj.workflow.do(decl.A)
        
        tasks = Task.objects.for_data(obj).filter(closed_at=None)
        self.failUnlessEqual(tasks[0].task_type.workflow_node, self.n_b)
        self.assertRaises(Task.DoesNotExist, tasks.get, task_type__workflow_node=self.n_a)

    def test_task_done(self):
        obj = Foo.objects.create()
        
        tasks = Task.objects.for_data(obj).filter(closed_at=None)
        self.failUnlessEqual(tasks[0].task_type.workflow_node, self.n_a)
        
        tasks[0].done()
        
        tasks = Task.objects.for_data(obj).filter(closed_at=None)
        self.failUnlessEqual(tasks[0].task_type.workflow_node, self.n_b)

    def test_task_trail(self):
        obj = Foo.objects.create()
        a_task = Task.objects.filter(closed_at=None).get()
        obj.workflow.do(decl.A)
        b_task = Task.objects.filter(closed_at=None).get()
        self.failUnlessEqual(set(b_task.trail), set([a_task]))

        