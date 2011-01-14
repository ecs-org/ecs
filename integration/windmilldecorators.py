# -*- coding: utf-8 -*-

from django.utils.functional import wraps
from windmill.authoring import WindmillTestClient


def logged_in(username='windmill@example.org', password='shfnajwg9e'):
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            client = WindmillTestClient(fn.__name__)
            
            client.click(id=u'id_username')
            client.type(text=username, id=u'id_username')
            client.click(id=u'id_password')
            client.type(text=password, id=u'id_password')
            client.click(value=u'login')
            client.waits.forPageLoad(timeout=u'20000')

            try:
                rval = fn(client, *args, **kwargs)
            finally:
                client.waits.forElement(link=u'Logout', timeout=u'8000')
                client.click(link=u'Logout')
                client.waits.forPageLoad(timeout=u'20000')

            return rval

        return decorated

    return decorator
    

def anonymous():
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            client = WindmillTestClient(fn.__name__)
            return fn(client, *args, **kwargs)
        return decorated
    return decorator
    

