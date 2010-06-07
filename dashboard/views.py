import re
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ecs.core.views.utils import render
from ecs.messages.models import Message, Thread
from ecs.tasks.models import Task

def view_dashboard(request):
    message_count = Message.objects.by_user(request.user).count()
    
    outgoing_threads = request.user.outgoing_threads.order_by('-timestamp')
    incoming_threads = request.user.incoming_threads.order_by('-timestamp')

    tasks = tasks = Task.objects.filter(closed_at=None)
    accepted_tasks = tasks.filter(assigned_to=request.user, accepted=True)
    assigned_tasks = tasks.filter(assigned_to=request.user, accepted=False)
    open_tasks = tasks.filter(assigned_to=None)
    
    return render(request, 'dashboard/dashboard.html', {
        'outgoing_threads': outgoing_threads,
        'incoming_threads': incoming_threads,
        'message_count': message_count,
        'accepted_tasks': accepted_tasks,
        'assigned_tasks': assigned_tasks,
        'open_tasks': open_tasks,
    })

def read_message(request, message_pk):
    message = get_object_or_404(Message.objects.by_user(request.user), pk=message_pk)
    if message.unread and message.receiver == request.user:
        message.unread = False
        message.save()
    return render(request, 'dashboard/read_message.html', {
        'message': message,
    })

