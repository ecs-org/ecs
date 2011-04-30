from ecs.utils.viewutils import render
from ecs.tasks.models import Task
from django.core.urlresolvers import reverse

def view_dashboard(request):
    widgets = [
        reverse('ecs.communication.views.outgoing_message_widget'),
        reverse('ecs.communication.views.incoming_message_widget'),
        reverse('ecs.core.views.submission_widget'),
    ]

    if request.user.get_profile().has_explicit_workflow():
        widgets.append(reverse('ecs.tasks.views.my_tasks'))

    return render(request, 'dashboard/dashboard.html', {
        'widgets': widgets,
    })

