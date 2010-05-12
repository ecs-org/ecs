from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from ecs.core.views import render, redirect_to_next_url
from ecs.tasks.models import Task

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
    tasks = Task.objects.filter(closed_at=None).order_by('-created_at')
    return render(request, 'tasks/backlog.html', {
        'tasks': tasks,
    })

def my_tasks(request):
    tasks = Task.objects.filter(closed_at=None)
    assigned_tasks = tasks #.filter(assigned_to=request.user)
    open_tasks = tasks.filter(assigned_to=None)
    return render(request, 'tasks/compact_list.html', {
        'assigned_tasks': tasks,
        'open_tasks': tasks,
    })

def accept_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
    task.accept(request.user)
    return redirect_to_next_url(request, reverse('ecs.tasks.my_tasks'))
    
def decline_task(request, task_pk=None):
    task = get_object_or_404(Task.objects.filter(assigned_to=request.user), pk=task_pk)
    task.assign(None)
    return redirect_to_next_url(request, reverse('ecs.tasks.my_tasks'))
    
def delegate_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
    user = get_object_or_404(User, pk=user_pk)
    task.assign(user)
    return redirect_to_next_url(request, reverse('ecs.tasks.my_tasks'))
    
def do_task(request, task_pk=None):
    task = get_object_or_404(Task, pk=task_pk)
    task.done()
    return redirect_to_next_url(request, reverse('ecs.tasks.my_tasks'))
