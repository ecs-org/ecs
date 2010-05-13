from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ecs.core.views import render, redirect_to_next_url
from ecs.tasks.models import Task
from ecs.tasks.forms import DelegateTaskForm

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
    tasks = Task.objects.filter(closed_at=None)
    try:
        submission_pk = int(request.GET['submission'])
    except (KeyError, ValueError):
        submission_pk = None
    if submission_pk:
        tasks = tasks.filter(content_type=ContentType.objects.get_for_model(Submission), data_id=submission_pk)

    accepted_tasks = tasks.filter(assigned_to=request.user, accepted=True)
    assigned_tasks = tasks.filter(assigned_to=request.user, accepted=False)
    open_tasks = tasks.filter(assigned_to=None)
    return render(request, 'tasks/compact_list.html', {
        'accepted_tasks': accepted_tasks,
        'assigned_tasks': assigned_tasks,
        'open_tasks': open_tasks,
    })

def accept_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
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
