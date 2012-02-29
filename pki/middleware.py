from urllib import urlencode
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

class ClientCertMiddleware(object):
    def process_request(self, request):
        require = getattr(settings, 'ECS_REQUIRE_CLIENT_CERTS', True)
        mandatory = getattr(settings, 'ECS_MANDATORY_CLIENT_CERTS', False)
        
        if (not require and not mandatory):
            return
        
        if request.user.is_authenticated():
            # nested to prevent premature imports
            url = reverse('ecs.pki.views.authenticate')
            if (request.path != url and (request.user.ecs_profile.is_internal or mandatory) 
                and not request.session.get('ecs_pki_authenticated', False)):
                return HttpResponseRedirect('%s?%s' % (url, urlencode({'next': request.get_full_path()})))
        
