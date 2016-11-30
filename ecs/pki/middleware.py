from django.conf import settings
from django.core.exceptions import PermissionDenied


class ClientCertMiddleware(object):
    def process_request(self, request):
        if not getattr(settings, 'ECS_REQUIRE_CLIENT_CERTS', False):
            return

        if request.user.is_authenticated():
            profile = request.user.profile
            if (profile.is_internal or profile.is_omniscient_member) and \
                request.META.get('HTTP_X_SSL_CLIENT_VERIFY') != 'SUCCESS':

                raise PermissionDenied()
