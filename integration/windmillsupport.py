# -*- coding: utf-8 -*-
import os

from django.utils.functional import wraps
from windmill.authoring import WindmillTestClient


## decorators ##

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


## HACK: dont look at this ##
def inject_firefox_plugins():
    from windmill.dep._mozrunner import get_moz as get_moz_orig
    from django.conf import settings

    def get_moz(*args, **kwargs):
        plugins = [os.path.join(settings.PROJECT_DIR, 'static', 'windmill', 'uploadassistant.xpi')]
        kwargs['settings']['MOZILLA_PLUGINS'] = kwargs['settings'].get('MOZILLA_PLUGINS', []) + plugins
        return get_moz_orig(*args, **kwargs)

    from windmill.dep import _mozrunner
    _mozrunner.get_moz = get_moz


