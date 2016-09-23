from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.decorators.cache import cache_control

from ecs.core.models import AdvancedSettings
from ecs.utils import forceauth


@forceauth.exempt
@cache_control(max_age=3600)
def logo(request):
    s = AdvancedSettings.objects.get()
    if not s.logo:
        return redirect(staticfiles_storage.url('images/fallback_logo.png'))
    return HttpResponse(s.logo, content_type=s.logo_mimetype)


@forceauth.exempt
def sitenotice(request):
    return render(request, 'sitenotice.html', {})
