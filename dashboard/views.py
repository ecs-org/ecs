from ecs.core.views.utils import render
from ecs.messages.models import Message
from django.shortcuts import get_object_or_404
from ecs.tasks.models import Task

def view_dashboard(request):
    return render(request, 'dashboard/dashboard.html', {
        'message_list': Message.objects.select_related('sender', 'receiver').filter(receiver=request.user).order_by('-timestamp'),
        'tasks': Task.objects.filter(closed_at=None, assigned_to=request.user, accepted=True),
    })

def read_message(request, message_pk):
    message = get_object_or_404(Message.objects.by_user(request.user), pk=message_pk)
    if message.unread and message.receiver == request.user:
        message.unread = False
        message.save()
    return render(request, 'dashboard/read_message.html', {
        'message': message,
    })
