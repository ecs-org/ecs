from urllib import urlencode
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class ClientCertMiddleware(object):
    def process_request(self, request):
        url = reverse('ecs.pki.views.authenticate')
        if request.path != url and request.user.is_authenticated() and request.user.ecs_profile.is_internal and not request.session.get('ecs_pki_authenticated', False):
            return HttpResponseRedirect('%s?%s' % (url, urlencode({'next': request.get_full_path()})))
        