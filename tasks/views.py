import random

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.users.utils import user_flag_required
from ecs.core.models import Submission
from ecs.communication.models import Thread
from ecs.tasks.models import Task
from ecs.tasks.forms import ManageTaskForm, TaskListFilterForm

@user_flag_required('internal')
def task_backlog(request, submission_pk=None, template='tasks/log.html'):
    tasks = Task.objects.order_by('created_at')
    if submission_pk:
        submission_ct = ContentType.objects.get_for_model(Submission)
        tasks = tasks.filter(content_type=submission_ct, data_id=submission_pk)
    return render(request, template, {
        'tasks': tasks,
    })

def my_tasks(request, template='tasks/compact_list.html'):
    usersettings = request.user.ecs_settings
    submission_ct = ContentType.objects.get_for_model(Submission)

    filter_defaults = {
        'sorting': 'deadline',
    }
    for key in ('amg', 'mpg', 'thesis', 'other', 'mine', 'assigned', 'open', 'proxy'):
        filter_defaults[key] = 'on'

    filterdict = request.POST or usersettings.task_filter or filter_defaults
    filterform = TaskListFilterForm(filterdict)
    filterform.is_valid() # force clean

    usersettings.task_filter = filterform.cleaned_data
    usersettings.save()
    
    all_tasks = Task.objects.for_user(request.user).filter(closed_at=None).select_related('task_type')
    sortings = {
        'deadline': 'workflow_token__deadline',
        'oldest': 'workflow_token__created_at',
        'newest': '-workflow_token__created_at',
    }
    order_by = ['task_type__name', sortings[filterform.cleaned_data['sorting'] or 'deadline'], 'assigned_at']

    all_tasks = Task.objects.for_user(request.user).filter(closed_at=None).select_related('task_type').order_by(*order_by)
    related_url = request.GET.get('url', None)
    if related_url:
        related_tasks = [t for t in all_tasks.filter(assigned_to=request.user, accepted=True) if t.url == related_url]
        if len(related_tasks) == 1:
            return HttpResponseRedirect(reverse('ecs.tasks.views.manage_task', kwargs={'task_pk': related_tasks[0].pk}))
        elif related_tasks:
            pass # XXX: how do we handle this case? (FMD2)

    try:
        submission_pk = int(request.GET['submission'])
    except (KeyError, ValueError):
        submission_pk = None

    if submission_pk:
        submission = get_object_or_404(Submission, pk=submission_pk)
        tasks = all_tasks.filter(content_type=submission_ct, data_id=submission_pk)
    else:
        submission = None
        amg = filterform.cleaned_data['amg']
        mpg = filterform.cleaned_data['mpg']
        thesis = filterform.cleaned_data['thesis']
        other = filterform.cleaned_data['other']
        if amg and mpg and thesis and other:
            tasks = all_tasks
        else:
            tasks = all_tasks.exclude(content_type=submission_ct)
            amg_q = Q(data_id__in=Submission.objects.amg().values('pk').query)
            mpg_q = Q(data_id__in=Submission.objects.mpg().values('pk').query)
            thesis_q = Q(data_id__in=Submission.objects.thesis().values('pk').query)
            submission_tasks = all_tasks.filter(content_type=submission_ct)
            if amg:
                tasks |= submission_tasks.filter(amg_q)
            if mpg:
                tasks |= submission_tasks.filter(mpg_q)
            if thesis:
                tasks |= submission_tasks.filter(thesis_q)
            if other:
                tasks |= submission_tasks.filter(~amg_q & ~mpg_q & ~thesis_q)

    data = {
        'submission': submission,
        'filterform': filterform,
        'form_id': 'task_list_filter_%s' % random.randint(1000000, 9999999),
    }

    task_flavors = {
        'mine': lambda tasks: tasks.filter(assigned_to=request.user, accepted=True),
        'assigned': lambda tasks: tasks.filter(assigned_to=request.user, accepted=False),
        'open': lambda tasks: tasks.filter(assigned_to=None),
        'proxy': lambda tasks: tasks.filter(assigned_to__ecs_profile__indisposed=True),
    }

    for key, func in task_flavors.items():
        context_key = '%s_tasks' % key
        data[context_key] = func(tasks) if filterform.cleaned_data[key] else tasks.none()

    return render(request, template, data)

def list(request):
    return my_tasks(request, template='tasks/list.html')
    
def manage_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
    form = ManageTaskForm(request.POST or None, task=task)
    if request.method == 'POST' and form.is_valid():
        action = form.cleaned_data['action']
        if action == 'complete':
            task.done(user=request.user, choice=form.get_choice())
        
        elif action == 'delegate':
            task.assign(form.cleaned_data['assign_to'])
        
        elif action == 'message':
            question_type = form.cleaned_data['question_type']
            if question_type == 'callback':
                to = form.cleaned_data['callback_task'].assigned_to
            elif question_type == 'somebody':
                to = form.cleaned_data['receiver']
            elif question_type == 'related':
                to = form.cleaned_data['related_task'].assigned_to
            message = Thread.objects.create(
                subject=u'Frage bzgl. %s' % task,
                submission=task.data, 
                task=task,
                text=form.cleaned_data['question'],
                sender=request.user,
                receiver=to,
            )
        return HttpResponseRedirect(reverse('ecs.tasks.views.my_tasks'))
    return render(request, 'tasks/manage_task.html', {
        'form': form,
        'task': task,
    })
    
def accept_task(request, task_pk=None):
    task = get_object_or_404(Task.objects.acceptable_for_user(request.user), pk=task_pk)
    task.accept(request.user)
    return redirect_to_next_url(request, reverse('ecs.tasks.views.my_tasks'))
    
def decline_task(request, task_pk=None):
    task = get_object_or_404(Task.objects.filter(assigned_to=request.user), pk=task_pk)
    task.assign(None)
    return redirect_to_next_url(request, reverse('ecs.tasks.views.my_tasks'))
    
def do_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
    task.done(request.user)
    return redirect_to_next_url(request, reverse('ecs.tasks.views.my_tasks'))
