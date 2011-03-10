import random

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
from ecs.communication.forms import TaskMessageForm
from ecs.tasks.models import Task
from ecs.tasks.forms import ManageTaskForm, TaskListFilterForm
from ecs.tasks.signals import task_accepted, task_declined


@user_flag_required('internal')
def task_backlog(request, submission_pk=None, template='tasks/log.html'):
    with sudo():
        tasks = Task.objects.order_by('created_at')
        if submission_pk:
            submission = get_object_or_404(Submission, pk=submission_pk)
            submission_ct = ContentType.objects.get_for_model(Submission)
            q = Q(content_type=submission_ct, data_id=submission.pk)
            vote_ct = ContentType.objects.get_for_model(Vote)
            q |= Q(content_type=vote_ct, data_id__in=Vote.objects.filter(submission_form__submission=submission).values('pk').query)
            meeting_ct = ContentType.objects.get_for_model(Meeting)
            q |= Q(content_type=meeting_ct, data_id__in=submission.meetings.values('pk').query)
            notification_ct = ContentType.objects.get_for_model(Notification)
            q |= Q(content_type=notification_ct, data_id__in=Notification.objects.filter(submission_forms__submission=submission).values('pk').query)
            tasks = tasks.filter(q)
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
        'oldest': '-created_at',
        'newest': 'created_at',
    }
    order_by = ['task_type__name', sortings[filterform.cleaned_data['sorting'] or 'deadline'], 'assigned_at']

    all_tasks = Task.objects.for_user(request.user).filter(closed_at=None)
    related_url = request.GET.get('url', None)
    if related_url:
        related_tasks = [t for t in all_tasks.filter(assigned_to=request.user, accepted=True) if related_url in t.get_final_urls()]
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
        'mine': lambda tasks: tasks.filter(assigned_to=request.user, accepted=True).order_by(*order_by),
        'assigned': lambda tasks: tasks.filter(assigned_to=request.user, accepted=False).order_by(*order_by),
        'open': lambda tasks: tasks.filter(assigned_to=None).order_by(*order_by),
        'proxy': lambda tasks: tasks.filter(assigned_to__ecs_profile__indisposed=True).order_by(*order_by),
    }

    for key, func in task_flavors.items():
        context_key = '%s_tasks' % key
        data[context_key] = func(tasks) if filterform.cleaned_data[key] else tasks.none()

    return render(request, template, data)

def list(request):
    return my_tasks(request, template='tasks/list.html')

def popup(request):
    return my_tasks(request, template='tasks/popup.html')
    
def manage_task(request, task_pk=None, full=False):
    task = get_object_or_404(Task, pk=task_pk)
    form = ManageTaskForm(request.POST or None, task=task)
    try:
        submission = task.data.get_submission()
    except AttributeError:
        submission = None
    message_form = TaskMessageForm(submission, request.user, request.POST or None, prefix='message')
    if request.method == 'POST' and form.is_valid():
        action = form.cleaned_data['action']
        if action == 'complete':
            task.done(user=request.user, choice=form.get_choice())
        
        elif action == 'delegate':
            task.assign(form.cleaned_data['assign_to'])
        
        elif action == 'message':
            if message_form.is_valid():
                thread = Thread.objects.create(
                    subject=_('Question regarding {0}').format(task),
                    submission=submission,
                    task=task,
                    sender=request.user,
                    receiver=message_form.cleaned_data['receiver'],
                )
                thread.add_message(request.user, text=message_form.cleaned_data['text'])
            else:
                return render(request, 'tasks/manage_task.html', {
                    'form': form,
                    'message_form': message_form,
                    'task': task,
                })

        if full:
            return HttpResponseRedirect(reverse('ecs.tasks.views.list'))
        else:
            return HttpResponseRedirect(reverse('ecs.tasks.views.my_tasks'))
    return render(request, 'tasks/manage_task.html', {
        'form': form,
        'message_form': message_form,
        'task': task,
    })
    
def manage_task_full(request, task_pk=None):
    return manage_task(request, task_pk=task_pk, full=True)

def accept_task(request, task_pk=None, full=False):
    task = get_object_or_404(Task.objects.acceptable_for_user(request.user), pk=task_pk)
    task.accept(request.user)
    task_accepted.send(type(task.node_controller), task=task)
    if full:
        return redirect_to_next_url(request, reverse('ecs.tasks.views.list'))
    else:
        return redirect_to_next_url(request, reverse('ecs.tasks.views.my_tasks'))

def accept_task_full(request, task_pk=None):
    return accept_task(request, task_pk=task_pk, full=True)

def decline_task(request, task_pk=None, full=False):
    task = get_object_or_404(Task.objects.filter(assigned_to=request.user), pk=task_pk)
    task.assign(None)
    task_declined.send(type(task.node_controller), task=task)
    if full:
        return redirect_to_next_url(request, reverse('ecs.tasks.views.list'))
    else:
        return redirect_to_next_url(request, reverse('ecs.tasks.views.my_tasks'))

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

