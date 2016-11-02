from django.shortcuts import redirect

from ecs.userswitcher.forms import UserSwitcherForm
from ecs.userswitcher import SESSION_KEY


def switch(request):
    form = UserSwitcherForm(request.POST)
    if form.is_valid():
        request.session[SESSION_KEY] = getattr(form.cleaned_data.get('user'), 'pk', None)
    # request.GET.get('url', '/')
    return redirect('ecs.dashboard.views.view_dashboard')
