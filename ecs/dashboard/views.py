from django.shortcuts import render
from django.core.urlresolvers import reverse

from ecs.utils.security import readonly


@readonly()
def view_dashboard(request):
    widgets = [
        reverse('ecs.communication.views.outgoing_message_widget'),
        reverse('ecs.communication.views.incoming_message_widget'),
        reverse('ecs.core.views.submissions.submission_widget'),
    ]

    if request.user.profile.has_explicit_workflow():
        widgets.append(reverse('ecs.tasks.views.my_tasks'))

    return render(request, 'dashboard/dashboard.html', {
        'widgets': widgets,
    })
