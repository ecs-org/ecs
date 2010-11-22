# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.utils.functional import wraps
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from ecs.users.middleware import current_user_store
from ecs.users.models import Invitation
from ecs.ecsmail.mail import deliver

def get_current_user():
    if hasattr(current_user_store, 'user'):
        return current_user_store.user
    else:
        return None
        
class sudo(object):
    def __init__(self, user=None):
        self.user = user

    def __enter__(self):
        from ecs.users.middleware import current_user_store
        self._previous_user = getattr(current_user_store, 'user', None)
        user = self.user
        if callable(user):
            user = user()
        current_user_store.user = user
        
    def __exit__(self, *exc):
        from ecs.users.middleware import current_user_store
        current_user_store.user = self._previous_user
        
    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return decorated


def user_flag_required(flag):
    return user_passes_test(lambda u: getattr(u.ecs_profile, flag, False))

