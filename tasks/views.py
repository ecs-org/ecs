# -*- coding: utf-8 -*-
import random
from urllib import urlencode

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.users.utils import user_flag_required, sudo
from ecs.core.models import Submission, Vote
from ecs.meetings.models import Meeting
from ecs.notifications.models import Notification
from ecs.communication.models import Thread
from ecs.tasks.models import Task
from ecs.tasks.forms import ManageTaskForm, TaskListFilterForm
from ecs.tasks.signals import task_accepted, task_declined


@user_flag_required('internal')
def task_backlog(request, submission_pk=None, template='tasks/log.html'):
    with sudo():
        tasks = Task.objects.all()
        if submission_pk:
            submission = get_object_or_404(Submission, pk=submission_pk)
            tasks = tasks.for_submission(submission)
        tasks = list(tasks.order_by('created_at'))

    return render(request, template, {
        'tasks': tasks,
    })


def my_tasks(request, template='tasks/compact_list.html', submission_pk=None):
    usersettings = request.user.ecs_settings
    submission_ct = ContentType.objects.get_for_model(Submission)

    filter_defaults = dict(sorting='deadline')
    for key in ('amg', 'mpg', 'thesis', 'expedited', 'other', 'mine', 'assigned', 'open', 'proxy'):
        filter_defaults[key] = 'on'

    filterdict = request.POST or request.GET or usersettings.task_filter or filter_defaults
    filterform = TaskListFilterForm(filterdict)
    filterform.is_valid() # force clean

    userfilter = filterform.cleaned_data.copy()
    del userfilter['task_types']
    if request.method == 'POST':
        usersettings.task_filter = userfilter
        usersettings.save()
        if len(request.GET.values()) > 0:
            return HttpResponseRedirect(request.path)
    
    sortings = {
        'deadline': 'workflow_token__deadline',
        'oldest': '-created_at',
        'newest': 'created_at',
    }
    order_by = ['task_type__name', sortings[filterform.cleaned_data['sorting'] or 'deadline'], 'assigned_at']

    all_tasks = Task.objects.for_widget(request.user).filter(closed_at__isnull=True).select_related('task_type')
    related_url = request.GET.get('url', None)
    if related_url:
        related_tasks = [t for t in all_tasks.filter(assigned_to=request.user, accepted=True) if related_url in t.get_final_urls()]
        if len(related_tasks) == 1:
            return HttpResponseRedirect(reverse('ecs.tasks.views.manage_task', kwargs={'task_pk': related_tasks[0].pk}))
        elif related_tasks:
            pass # XXX: how do we handle this case? (FMD2)

    if submission_pk:
        submission = get_object_or_404(Submission, pk=submission_pk)
        tasks = all_tasks.for_submission(submission)
    else:
        submission = None
        amg = filterform.cleaned_data['amg']
        mpg = filterform.cleaned_data['mpg']
        thesis = filterform.cleaned_data['thesis']
        expedited = filterform.cleaned_data['expedited']
        other = filterform.cleaned_data['other']
        if amg and mpg and thesis and expedited and other:
            tasks = all_tasks
        else:
            tasks = all_tasks.exclude(content_type=submission_ct)
            amg_q = Q(data_id__in=Submission.objects.amg().values('pk').query)
            mpg_q = Q(data_id__in=Submission.objects.mpg().values('pk').query)
            retrospective_thesis_q = Q(data_id__in=Submission.objects.retrospective_thesis().values('pk').query)
            expedited_q = Q(data_id__in=Submission.objects.filter(expedited=True))
            submission_tasks = all_tasks.filter(content_type=submission_ct)
            if amg:
                tasks |= submission_tasks.filter(amg_q)
            if mpg:
                tasks |= submission_tasks.filter(mpg_q)
            if thesis:
                tasks |= submission_tasks.filter(retrospective_thesis_q)
            if expedited:
                tasks |= submission_tasks.filter(expedited_q)
            if other:
                tasks |= submission_tasks.filter(~amg_q & ~mpg_q & ~retrospective_thesis_q & ~expedited_q)
    
        task_types = filterform.cleaned_data['task_types']
        if task_types:
            tasks = tasks.filter(task_type__in=task_types)

    data = {
        'submission': submission,
        'filterform': filterform,
        'form_id': 'task_list_filter_%s' % random.randint(1000000, 9999999),
        'bookmarklink': '{0}?{1}'.format(request.build_absolute_uri(request.path), urlencode(userfilter)),
    }

    task_flavors = {
        'mine': lambda tasks: tasks.filter(assigned_to=request.user, accepted=True).order_by(*order_by),
        'assigned': lambda tasks: tasks.filter(assigned_to=request.user, accepted=False).order_by(*order_by),
        'open': lambda tasks: tasks.filter(assigned_to=None).order_by(*order_by),
        'proxy': lambda tasks: tasks.filter(assigned_to__ecs_profile__indisposed=True).order_by(*order_by),
    }

    for k, f in task_flavors.iteritems():
        ck = '%s_tasks' % k
        data[ck] = f(tasks) if filterform.cleaned_data[k] else tasks.none()

    return render(request, template, data)

def task_list(request, **kwargs):
    kwargs.setdefault('template', 'tasks/list.html')
    return my_tasks(request, **kwargs)
    
def manage_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
    form = ManageTaskForm(request.POST or None, task=task)
    try:
        submission = task.data.get_submission()
    except AttributeError:
        submission = None

    if request.method == 'POST' and form.is_valid():
        action = form.cleaned_data['action']
        if action == 'complete':
            task.done(user=request.user, choice=form.get_choice())
        elif action == 'delegate':
            task.assign(form.cleaned_data['assign_to'])
        else:
            raise Http404()

        if isinstance(task.data, Submission):
            return render(request, 'tasks/js_redirect.html', {'task': task, 'url': reverse('ecs.core.views.submissions.readonly_submission_form', kwargs={'submission_form_pk': submission.current_submission_form.pk})})
        return render(request, 'tasks/js_redirect.html', {'task': task, 'url': reverse('ecs.tasks.views.task_list')})
    return render(request, 'tasks/manage_task.html', {
        'form': form,
        'task': task,
    })

def accept_task(request, task_pk=None, full=False):
    task = get_object_or_404(Task.objects.acceptable_for_user(request.user), pk=task_pk)
    task.accept(request.user)
    task_accepted.send(type(task.node_controller), task=task)

    submission_pk = request.GET.get('submission')
    view = 'ecs.tasks.views.task_list' if full else 'ecs.tasks.views.my_tasks'
    return redirect_to_next_url(request, reverse(view, kwargs={'submission_pk': submission_pk} if submission_pk else None))

def accept_task_full(request, task_pk=None):
    return accept_task(request, task_pk=task_pk, full=True)

def decline_task(request, task_pk=None, full=False):
    task = get_object_or_404(Task.objects.filter(assigned_to=request.user), pk=task_pk)
    task.assign(None)
    task_declined.send(type(task.node_controller), task=task)

    submission_pk = request.GET.get('submission')
    view = 'ecs.tasks.views.task_list' if full else 'ecs.tasks.views.my_tasks'
    return redirect_to_next_url(request, reverse(view, kwargs={'submission_pk': submission_pk} if submission_pk else None))

def decline_task_full(request, task_pk=None):
    return decline_task(request, task_pk=task_pk, full=True)

def reopen_task(request, task_pk=None):
    task = get_object_or_404(Task.objects.filter(assigned_to=request.user), pk=task_pk)
    if task.workflow_token.workflow.is_finished:
        raise Http404()
    if not task.node_controller.is_repeatable():
        raise Http404()
    new_task = task.reopen(user=request.user)
    return HttpResponseRedirect(new_task.url)

