# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from ecs.users.middleware import current_user_store

def get_current_user():
    if hasattr(current_user_store, 'user'):
        return current_user_store.user
    else:
        return User.objects.get(username='root')
