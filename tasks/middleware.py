# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, QueryDict
from django.core.urlresolvers import reverse

from ecs.tasks.models import Task

class TaskManagementData(object):
    def __init__(self, request):
        self.request = request
        self.method = request.method
        self.POST = request.POST
        self.submit = self.POST.get('task_management-submit')
        self.save = self.POST.get('task_management-save')
        try:
            first = request.related_tasks[0]
            self.task_pk = first.pk if not first.managed_transparently else None
        except IndexError:
            self.task_pk = None
        self._form = None

        if self.task_pk is not None and self.method == 'POST':
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
        if self.task_pk:
            # refetch task instance to get an up-to-date task.data object. If we don't refetch the data
            # there might be inconsistencies in the database records, because task.data might have changed
            return Task.objects.get(pk=self.task_pk)
        else:
            return None

    @property
    def form(self):
        from ecs.tasks.forms import ManageTaskForm
        # Do not create the form until it is accessed
        if self._form is not None:
            return self._form
        else:
            form = None
            task = self.task
            if task:
                form = ManageTaskForm(None, task=task, prefix='task_management')
                if self.method == 'POST' and self.submit:
                    form = ManageTaskForm(self.POST or None, task=task, prefix='task_management')
                    form.is_valid()     # validate form, so errors are displayed
            self._form = form
            return form

    def process_response(self, response):
        task = self.task
        form = self.form
        if form and self.method == 'POST' and self.submit and form.is_valid():
            action = form.cleaned_data['action']
            if action == 'complete':
                task.done(user=self.request.user, choice=form.get_choice())
            elif action == 'delegate':
                task.assign(form.cleaned_data['assign_to'])
            try:
                submission = task.data.get_submission()
            except AttributeError:
                return HttpResponseRedirect(reverse('ecs.tasks.views.task_list'))
            else:
                return HttpResponseRedirect(reverse('ecs.core.views.submissions.readonly_submission_form',
                    kwargs={'submission_form_pk': submission.current_submission_form.pk}))
        return response

class RelatedTasksMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        user_tasks = Task.objects.for_user(request.user).filter(closed_at__isnull=True).select_related('task_type')
        accepted_tasks = user_tasks.filter(assigned_to=request.user, accepted=True, deleted_at=None)
        request.related_tasks =  [t for t in accepted_tasks if request.path in t.get_final_urls()]

        request.task_management = TaskManagementData(request)

    def process_response(self, request, response):
        if hasattr(request, 'task_management'):
            return request.task_management.process_response(response)
        else:
            return response
