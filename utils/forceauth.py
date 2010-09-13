#
# (c) 2010 MedUni Wien
#
"""
Middleware that forces Authentication.
"""
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

def exempt(view):
    view._forceauth_exempt = True
    return view

class ForceAuth:
    def process_view(self, request, view, args, kwargs):
        if not getattr(view, '_forceauth_exempt', False) and request.user.is_anonymous():
            return HttpResponseRedirect(settings.LOGIN_URL + '?next=%s' % request.path)

