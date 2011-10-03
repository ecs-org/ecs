# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, QueryDict
from django.core.urlresolvers import reverse

from ecs.tasks.models import Task
from ecs.tasks.forms import ManageTaskForm

class RelatedTasksMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        user_tasks = Task.objects.for_widget(request.user).filter(closed_at__isnull=True).select_related('task_type')
        accepted_tasks = user_tasks.filter(assigned_to=request.user, accepted=True, deleted_at=None)
        request.related_tasks =  [t for t in accepted_tasks if request.path in t.get_final_urls()]

        if request.related_tasks:
            task = request.related_tasks[0]     # we pretend, that there can only be one related task
            form = ManageTaskForm(None, task=task, prefix='task_management')
            request.original_POST = request.POST
            request.original_method = request.method
            if request.method == 'POST':
                submit = request.POST.get('task_management-submit')
                save = request.POST.get('task_management-save')
                if submit:
                    form = ManageTaskForm(request.POST or None, task=task, prefix='task_management')
                    form.is_valid()     # validate form, so errors are displayed
                if submit or save:
                    post_data = request.POST.get('task_management-post_data', '')
                    request.POST = QueryDict(post_data, encoding=request.POST.encoding)
                    # if there is no post_data, we pretend that the request is a GET request, so
                    # forms in the view don't show errors
                    if not post_data:
                        request.method = 'GET'
            request.task_management_form = form

    def process_response(self, request, response):
        form = getattr(request, 'task_management_form', None)
        if form and request.original_method == 'POST' and request.original_POST.get('task_management-submit') and form.is_valid():
            action = form.cleaned_data['action']
            # refetch task instance to get an up-to-date task.data object. If we don't refetch the data
            # there might be inconsistencies in the database records, because task.data might have changed
            task = Task.objects.get(pk=form.task.pk)
            if action == 'complete':
                task.done(user=request.user, choice=form.get_choice())
            elif action == 'delegate':
                task.assign(form.cleaned_data['assign_to'])
            if hasattr(task.data, 'get_submission'):
                submission = task.data.get_submission()
                return HttpResponseRedirect(reverse('ecs.core.views.submissions.readonly_submission_form', kwargs={'submission_form_pk': submission.current_submission_form.pk}))
            else:
                return HttpResponseRedirect(reverse('ecs.tasks.views.task_list'))
        return response
