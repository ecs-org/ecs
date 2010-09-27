from django.core import management
from ecs.utils.testcases import EcsTestCase
from ecs.workflow.controllers import clear_caches

class WorkflowTestCase(EcsTestCase):
    def setUp(self):
        super(WorkflowTestCase, self).setUp()
        clear_caches()
        management.call_command('workflow_sync')
        
    def tearDown(self):
        clear_caches()
        super(WorkflowTestCase, self).tearDown()

    def assertActivitiesEqual(self, obj, acts):
        self.failUnlessEqual(set(acts), set(type(act) for act in obj.workflow.activities))

