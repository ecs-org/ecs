#
# (c) 2010 MedUni Wien
#
"""
Middleware that forces Authentication.
"""

from django.contrib.auth.views import login
from django.http import HttpResponseRedirect

class ForceAuth:
    def process_request(self, request):
        if not request.path.startswith('/accounts/login/') and "/js/" not in request.path and "/css/" not in request.path and request.user.is_anonymous():
            if request.POST:
                return login(request)
            else:
                return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)

