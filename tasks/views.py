from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.core.models import Submission
from ecs.communication.models import Thread
from ecs.tasks.models import Task
from ecs.tasks.forms import DelegateTaskForm, ManageTaskForm, TaskListFilterForm

def task_list(request, user=None, data=None):
    tasks = Task.objects.filter(closed_at=None)
    if data:
        tasks = tasks.filter(data=data)
    if user:
        tasks = tasks.filter(assigned_to=user)
    return render(request, 'tasks/list.html', {
        'tasks': tasks,
    })
    
def task_backlog(request):
    tasks = Task.objects.order_by('-closed_at', '-created_at')
    return render(request, 'tasks/backlog.html', {
        'tasks': tasks,
    })

def my_tasks(request):
    all_tasks = Task.objects.for_user(request.user).filter(closed_at=None).select_related('task_type').order_by('task_type__name', '-assigned_at')
    related_url = request.GET.get('url', None)
    if related_url:
        related_tasks = [t for t in all_tasks.filter(assigned_to=request.user, accepted=True) if t.url == related_url]
        if len(related_tasks) == 1:
            return HttpResponseRedirect(reverse('ecs.tasks.views.manage_task', kwargs={'task_pk': related_tasks[0].pk}))
        elif related_tasks:
            pass # XXX: how do we handle this case?

    submission_ct = ContentType.objects.get_for_model(Submission)
    taskfilter_session_key = 'tasks:filter'
    filterform = TaskListFilterForm(request.POST or request.session.get(taskfilter_session_key, {'amg': True, 'mpg': True, 'other': True, 'mine': True, 'open': True, 'proxy': True}))
    filterform.is_valid() # force clean
    request.session[taskfilter_session_key] = filterform.cleaned_data
    
    try:
        submission_pk = int(request.GET['submission'])
    except (KeyError, ValueError):
        submission_pk = None
    if submission_pk:
        tasks = all_tasks.filter(content_type=submission_ct, data_id=submission_pk)
    else:
        amg = filterform.cleaned_data['amg']
        mpg = filterform.cleaned_data['mpg']
        other = filterform.cleaned_data['other']
        if amg and mpg and other:
            tasks = all_tasks
        else:
            tasks = all_tasks.exclude(content_type=submission_ct)
            amg_q = Q(data_id__in=Submission.objects.amg().values('pk').query)
            mpg_q = Q(data_id__in=Submission.objects.mpg().values('pk').query)
            submission_tasks = all_tasks.filter(content_type=submission_ct)
            if amg:
                tasks |= submission_tasks.filter(amg_q)
            if mpg:
                tasks |= submission_tasks.filter(mpg_q)
            if other:
                tasks |= submission_tasks.filter(~amg_q & ~mpg_q)

    if filterform.cleaned_data['mine']:
        accepted_tasks = tasks.filter(assigned_to=request.user, accepted=True)
        assigned_tasks = tasks.filter(assigned_to=request.user, accepted=False)
    else:
        accepted_tasks = tasks.none()
        assigned_tasks = tasks.none()

    if filterform.cleaned_data['open']:
        open_tasks = tasks.filter(assigned_to=None)
    else:
        open_tasks = tasks.none()
        
    if filterform.cleaned_data['proxy']:
        proxy_tasks = tasks.filter(assigned_to__ecs_profile__indisposed=True)
    else:
        proxy_tasks = tasks.none()

    return render(request, 'tasks/compact_list.html', {
        'accepted_tasks': accepted_tasks,
        'assigned_tasks': assigned_tasks,
        'open_tasks': open_tasks,
        'proxy_tasks': proxy_tasks,
        'filterform': filterform,
    })
    
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
    
def delegate_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
    form = DelegateTaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task.assign(form.cleaned_data['user'])
        return redirect_to_next_url(request, reverse('ecs.tasks.views.my_tasks'))
    return render(request, 'tasks/delegate.html', {
        'form': form,
    })
    
def do_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
    task.done(request.user)
    return redirect_to_next_url(request, reverse('ecs.tasks.views.my_tasks'))
