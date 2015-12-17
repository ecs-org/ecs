from ecs.utils.testcases import LoginTestCase
from ecs.workflow.tests import WorkflowTestCase
from django.core.urlresolvers import reverse
from ecs.tasks.models import Task, TaskType

class ViewTestCase(LoginTestCase, WorkflowTestCase):
    '''Tests for the tasks and workflow module
    
    Tests for the common workflow functionalities via the tasks module views.
    '''
    
    def test_common_workflow(self):
        '''Tests task list, task list filter, accepting of a task, task management view, task delegation back to the task pool,
        task reassignment and completion of a task.
        '''
        
        task_type = TaskType.objects.create(name="TestTask")
        task = Task.objects.create(task_type=task_type)
        refetch = lambda: Task.objects.get(pk=task.pk)

        # show the task list
        response = self.client.get(reverse('ecs.tasks.views.my_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(task in response.context['open_tasks'])
        
        # change the task list filter
        response = self.client.post(reverse('ecs.tasks.views.my_tasks'), {'proxy': False, 'mine': True, 'open': True, 'amg': False, 'mpg': False, 'other': True})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(task in response.context['open_tasks'])
        
        # accept the task
        response = self.client.post(reverse('ecs.tasks.views.accept_task', kwargs={'task_pk': task.pk}))
        task = refetch()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user, task.assigned_to)
        self.assertFalse(task.assigned_at is None)
        self.assertFalse(not task.accepted)
