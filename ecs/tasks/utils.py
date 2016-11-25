from functools import wraps

from django.shortcuts import redirect
from django.http import QueryDict
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from ecs.tasks.models import Task
from ecs.tasks.forms import ManageTaskForm
from ecs.users.utils import sudo


def get_obj_tasks(activities, obj, data=None):
    tasks = Task.objects.filter(workflow_token__in=obj.workflow.tokens.filter(node__node_type__in=[a._meta.node_type for a in activities]).values('pk').query, deleted_at=None)
    if data:
        tasks = tasks.filter(workflow_token__node__data_id=data.pk, workflow_token__node__data_ct=ContentType.objects.get_for_model(type(data)))
    return tasks


def block_if_task_exists(node_uid, **kwargs):
    ''' workflow guard decorator for tasks which should only be started once '''
    def _decorator(func):
        @wraps(func)
        def _inner(wf):
            with sudo():
                if Task.objects.for_data(wf.data).filter(task_type__workflow_node__uid=node_uid, **kwargs).exists():
                    return False
            return func(wf)
        return _inner
    return _decorator

def block_duplicate_task(node_uid):
    return block_if_task_exists(node_uid, deleted_at=None, closed_at=None)

def task_required(view):
    @wraps(view)
    def _inner(request, *args, **kwargs):
        if not getattr(request, 'related_tasks', None):
            raise PermissionDenied()
        return view(request, *args, **kwargs)
    return _inner

def with_task_management(view):
    @wraps(view)
    def _inner(request, *args, **kwargs):
        request.task_management = TaskManagementData(request)
        response = view(request, *args, **kwargs)
        return request.task_management.process_response(response)
    return _inner

class TaskManagementData(object):
    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.method = request.method
        self.POST = request.POST
        self.submit = 'task_management-action' in self.POST
        self.save = self.POST.get('task_management-save')

        if request.method == 'POST' and not self.task is None:
            if self.submit or self.save:
                post_data = self.POST.get('task_management-post_data', '')
                # QueryDict only reliably works with bytestrings, so we encode `post_data` again (see #2978).
                request.POST = QueryDict(post_data.encode('utf-8'), encoding='utf-8')
                # if there is no post_data, we pretend that the request is a GET request, so
                # forms in the view don't show errors
                if not post_data:
                    request.method = 'GET'

    @property
    def task(self):
        if not hasattr(self, '_task_pk'):
            try:
                first = self.request.related_tasks[0]
                self._task_pk = first.pk if not first.managed_transparently else None
            except IndexError:
                self._task_pk = None

        task = None
        if not self._task_pk is None:
            # refetch
            task = Task.objects.get(pk=self._task_pk)
        return task

    @property
    def form(self):
        if not hasattr(self, '_form'):
            form = None
            task = self.task
            if task:
                form = ManageTaskForm(None, task=task, user=self.user,
                    prefix='task_management')
                if self.method == 'POST' and self.submit:
                    form = ManageTaskForm(self.POST or None, task=task,
                        user=self.user, prefix='task_management')
                    form.is_valid()     # validate form, so errors are displayed
            self._form = form
        return self._form

    def process_response(self, response):
        if self.method == 'POST' and self.form and self.form.is_valid() and self.submit:
            task = self.task
            action = self.form.cleaned_data['action']
            if action == 'complete':
                if getattr(response, 'has_errors', False):
                    return response
                task.done(user=self.request.user, choice=self.form.get_choice())
                task = self.task    # refetch
            elif action == 'delegate':
                task.assign(self.form.cleaned_data['assign_to'])

            url = task.afterlife_url
            if url is None:     # FIXME: use afterlife_url for all activities
                try:
                    submission = task.data.get_submission()
                except AttributeError:
                    submission = None
                if submission:
                    url = reverse('view_submission', kwargs={'submission_pk': submission.pk})
                else:
                    if self.request.user.profile.show_task_widget:
                        url = reverse('ecs.tasks.views.task_list')
                    else:
                        url = reverse('ecs.dashboard.views.view_dashboard')
            return redirect(url)
        return response
