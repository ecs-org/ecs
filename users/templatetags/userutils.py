from django.template import Library

register = Library()

@register.filter
def has_flag(user, flag):
    return getattr(user.ecs_profile, flag, False)

@register.filter
def is_member_of(user, groupname):
    return bool(user.groups.filter(name=groupname).count())

