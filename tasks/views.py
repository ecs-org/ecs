from ecs.core.views import render
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