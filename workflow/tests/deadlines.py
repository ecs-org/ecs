from datetime import timedelta
from django.test import TestCase
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core import management

from ecs.workflow.models import Graph, Node
from ecs import workflow

class DeadFoo(models.Model):
    flag = models.BooleanField(default=False)

    class Meta:
        app_label='workflow'

workflow.register(DeadFoo)

a = workflow.declare_activity(DeadFoo, 'do_a', deadline=timedelta(seconds=0))
b = workflow.declare_activity(DeadFoo, 'do_b')
c = workflow.declare_activity(DeadFoo, 'do_c')

def _flag_test(wf):
    return wf.data.flag

flag_test = workflow.declare_guard(DeadFoo, 'flag_set', _flag_test)

class DeadlineTest(TestCase):
    def setUp(self):
        management.call_command('workflow_sync')
        self.deadfoo_ct = ContentType.objects.get_for_model(DeadFoo)
        
    def assertActivitiesEqual(self, obj, acts):
        self.failUnlessEqual(acts, [bound_activity.activity for bound_activity in obj.workflow.activities])
        
    def test_simple_deadline(self):
        g = Graph.objects.create(name='TestGraph', content_type=self.deadfoo_ct, auto_start=True)
        n_a = g.create_node(a, start=True)
        n_b = g.create_node(b, end=True)
        n_c = g.create_node(c, end=True)
        n_a.add_edge(n_b)
        n_a.add_edge(n_c, deadline=True)
        
        # a, b
        obj = DeadFoo.objects.create()
        
        self.assertActivitiesEqual(obj, [a])
        obj.workflow.do(a)
        
        self.assertActivitiesEqual(obj, [b])
        obj.workflow.do(b)
        
        self.assertActivitiesEqual(obj, [])
        
        # a[deadline], c
        
        obj = DeadFoo.objects.create()
        self.assertActivitiesEqual(obj, [a])
        token = obj.workflow.get_token(a)
        token.handle_deadline()
        
        self.assertActivitiesEqual(obj, [c])
        obj.workflow.do(c)
        
        self.assertActivitiesEqual(obj, [])

