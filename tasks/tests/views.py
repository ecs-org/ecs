from ecs.utils.testcases import LoginTestCase
from ecs.workflow.tests import WorkflowTestCase
from django.core.urlresolvers import reverse
from ecs.tasks.models import Task, TaskType

class ViewTestCase(LoginTestCase, WorkflowTestCase):
    '''Task workflow tests.'''
    
    def test_common_workflow(self):
        '''Tests task list, task list filter, accepting of a task, task management view task delegation back to the task pool, task reassignment and completion of a task.'''
        
        task_type = TaskType.objects.create(name="TestTask")
        task = Task.objects.create(task_type=task_type)
        refetch = lambda: Task.objects.get(pk=task.pk)

        # show the task list
        response = self.client.get(reverse('ecs.tasks.views.my_tasks'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(task in response.context['open_tasks'])
        
        # change the task list filter
        response = self.client.post(reverse('ecs.tasks.views.my_tasks'), {'proxy': False, 'mine': True, 'open': True, 'amg': False, 'mpg': False, 'other': True})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(task in response.context['open_tasks'])
        
        # accept the task
        response = self.client.get(reverse('ecs.tasks.views.accept_task', kwargs={'task_pk': task.pk}))
        task = refetch()
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(self.user, task.assigned_to)
        self.failIf(task.assigned_at is None)
        self.failIf(not task.accepted)
        
        # get the task management view
        manage_task_url = reverse('ecs.tasks.views.manage_task', kwargs={'task_pk': task.pk})
        response = self.client.get(manage_task_url)
        self.failUnlessEqual(response.status_code, 200)
        
        # delegate the task back to the pool
        response = self.client.post(manage_task_url, {'action': 'delegate', 'assign_to': ''})
        self.failUnlessEqual(response.status_code, 302)
        task = refetch()
        self.failUnless(task.assigned_to is None)
        
        # reassign the user and complete the task
        task.accept(self.user)
        response = self.client.post(manage_task_url, {'action': 'complete'})
        self.failUnlessEqual(response.status_code, 302)
        task = refetch()
        self.failIf(task.closed_at is None)
        self.failIf(not task.accepted)
        
        
