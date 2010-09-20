# -*- coding: utf-8 -*-
from contextlib import contextmanager
from django.contrib.auth.models import User

from ecs.users.middleware import current_user_store

def get_current_user():
    if hasattr(current_user_store, 'user'):
        return current_user_store.user
    else:
        return None
        # FIXME: what do we return during testing or management commands? Do we really query the user table every time?
        #return User.objects.get(username='root')
        
@contextmanager
def sudo(user):
    from ecs.users.middleware import current_user_store
    _previous_user = getattr(current_user_store, 'user', None)
    current_user_store.user = user
    yield
    current_user_store = _previous_user
