# -*- coding: utf-8 -*-

from django.template import Library

from ecs.users.utils import get_formal_name


register = Library()

@register.filter
def has_flag(user, flag):
    return getattr(user.ecs_profile, flag, False)

@register.filter
def is_member_of(user, groupname):
    return bool(user.groups.filter(name=groupname).count())

@register.filter
def formal_name(user):
    return get_formal_name(user)

