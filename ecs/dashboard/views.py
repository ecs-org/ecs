from django.shortcuts import render

from ecs.utils.security import readonly


@readonly()
def view_dashboard(request):
    return render(request, 'dashboard/dashboard.html')
