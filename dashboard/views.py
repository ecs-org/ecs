from ecs.core.views.utils import render
from ecs.messages.models import Message

def view_dashboard(request):
    return render(request, 'dashboard/dashboard.html', {
        'message_list': Message.objects.select_related('sender', 'receiver').filter(receiver=request.user).order_by('-timestamp'),
    })


