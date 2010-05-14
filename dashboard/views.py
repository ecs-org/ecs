import re
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ecs.core.views.utils import render
from ecs.messages.models import Message
from ecs.messages.utilitys import strip_subject, get_threads
from ecs.tasks.models import Task

def view_dashboard(request):
    messages = Message.objects.select_related('sender', 'receiver').filter(Q(receiver=request.user)|Q(sender=request.user)).order_by('-timestamp')
    message_count = messages.count()
    threads = get_threads(messages)
    tasks = tasks = Task.objects.filter(closed_at=None)
    accepted_tasks = tasks.filter(assigned_to=request.user, accepted=True)
    assigned_tasks = tasks.filter(assigned_to=request.user, accepted=False)
    open_tasks = tasks.filter(assigned_to=None)
    
    return render(request, 'dashboard/dashboard.html', {
        'threads': threads,
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
