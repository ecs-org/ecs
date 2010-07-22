import time
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.functional import wraps
from ecs.utils.django_signed import signed

HASH_AUTH_GETVAR = getattr(settings, 'HASH_AUTH_GETVAR', 'ecsauth')

def _get_timestamp():
    return int(time.time())

class HashAuthView(object):
    def __init__(self, view, ttl=300):
        self.view = view
        self.ttl = ttl
        
    def __call__(self, request, *args, **kwargs):
        token = request.GET.get(HASH_AUTH_GETVAR, '')
        try:
            timestamp = signed.loads(token, extra_key=request.path)
        except signed.BadSignature:
            return HttpResponseForbidden("invalid token")
        if _get_timestamp() - timestamp > self.ttl:
            return HttpResponseForbidden("token expired")
        return self.view(request, *args, **kwargs)


def protect(**kwargs):
    def decorator(view):
        return wraps(view)(HashAuthView(view, **kwargs))
    return decorator
    
def sign_url(url):
    token = signed.dumps(_get_timestamp(), extra_key=url)
    return "%s?%s=%s" % (url, HASH_AUTH_GETVAR, token)
