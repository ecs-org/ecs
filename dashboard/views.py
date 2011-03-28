from ecs.utils.viewutils import render
from ecs.tasks.models import Task
from django.core.urlresolvers import reverse

def view_dashboard(request):
    widgets = [
        reverse('ecs.communication.views.outgoing_message_widget'),
        reverse('ecs.communication.views.incoming_message_widget'),
    ]

    if request.user.groups.exclude(name__in=[u'Presenter', u'Sponsor', u'Investigator', u'External Reviewer', u'userswitcher_target']).count():
        widgets.append(reverse('ecs.tasks.views.my_tasks'))

    if request.user.ecs_profile.internal:
        widgets.append(reverse('ecs.core.views.submission_widget'))

    return render(request, 'dashboard/dashboard.html', {
        'widgets': widgets,
    })

