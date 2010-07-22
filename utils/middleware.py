from ecs.utils.django_signed import signed

from django.conf import settings

SIGNED_COOKIE_SECRET = getattr(settings, 'SIGNED_COOKIE_SECRET', '')

class SignedCookiesMiddleware(object):
    def process_request(self, request):
        for name, signed_value in request.COOKIES.items():
            try:
                signed_name, user_pk, value = signed.loads(signed_value, extra_key=SIGNED_COOKIE_SECRET)
                if user_pk != getattr(request.user, 'pk', None) or signed_name != name:
                    raise ValueError()
                request.COOKIES[name] = value
            except (signed.BadSignature, ValueError):
                del request.COOKIES[name]
    
    def process_response(self, request, response):
        for name, morsel in response.cookies.items():
            if morsel['max-age'] == 0:
                # Deleted cookies don't need to be signed
                continue
            response.set_cookie(name, signed.dumps((name, getattr(request.user, 'pk', None), morsel.value), extra_key=SIGNED_COOKIE_SECRET),
                max_age=morsel['max-age'],
                expires=morsel['expires'],
                path=morsel['path'],
                domain=morsel['domain'],
                secure=morsel['secure']
            )
        return response