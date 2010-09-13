from ecs.core.views.utils import render
from ecs.tasks.models import Task

def view_dashboard(request):
    tasks = tasks = Task.objects.filter(closed_at=None)
    accepted_tasks = tasks.filter(assigned_to=request.user, accepted=True)
    assigned_tasks = tasks.filter(assigned_to=request.user, accepted=False)
    open_tasks = tasks.filter(assigned_to=None)
    
    return render(request, 'dashboard/dashboard.html', {
        'accepted_tasks': accepted_tasks,
        'assigned_tasks': assigned_tasks,
        'open_tasks': open_tasks,
    })
    