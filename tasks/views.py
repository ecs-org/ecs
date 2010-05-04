from ecs.core.views import render

def task_list(request, user=None, data=None):
    tasks = Task.objects.all(closed_at=None)
    if data:
        tasks = tasks.filter(data=data)
    if user:
        tasks = tasks.filter(assigned_to=user)
    return render(request, 'tasks/list.html', {
        'tasks': tasks,
    })
