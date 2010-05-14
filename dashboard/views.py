import re
from django.shortcuts import get_object_or_404
from ecs.core.views.utils import render
from ecs.messages.models import Message
from ecs.tasks.models import Task


def sort_by_thread(messages):
    threads = {}
    for message in messages:
        subject = re.match('([Rr][Ee]:\s*)?(.*)', message.subject).group(2).strip()
        try:
            threads[subject].append(message)
        except KeyError:
            threads[subject] = [message]
    
    print [{'subject': x, 'messages': threads[x]} for x in threads]
    
    return [{'subject': x, 'messages': threads[x]} for x in threads]


def view_dashboard(request):
    messages = Message.objects.select_related('sender', 'receiver').filter(receiver=request.user).order_by('-timestamp')
    message_count = messages.count()
    threads = sort_by_thread(messages)
    tasks = Task.objects.filter(closed_at=None, assigned_to=request.user, accepted=True)
    
    return render(request, 'dashboard/dashboard.html', {
        'threads': threads,
        'message_count': message_count,
        'tasks': tasks,
    })

def read_message(request, message_pk):
    message = get_object_or_404(Message.objects.by_user(request.user), pk=message_pk)
    if message.unread and message.receiver == request.user:
        message.unread = False
        message.save()
    return render(request, 'dashboard/read_message.html', {
        'message': message,
    })
