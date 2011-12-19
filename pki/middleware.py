from urllib import urlencode
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

class ClientCertMiddleware(object):
    def process_request(self, request):
        url = reverse('ecs.pki.views.authenticate')
        if not getattr(settings, 'ECS_REQUIRE_CLIENT_CERTS', True):
            return
        if request.path != url and request.user.is_authenticated() and request.user.ecs_profile.is_internal and not request.session.get('ecs_pki_authenticated', False):
            return HttpResponseRedirect('%s?%s' % (url, urlencode({'next': request.get_full_path()})))
        