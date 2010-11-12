from django.template import Library

register = Library()

@register.filter
def has_flag(user, flag):
    return getattr(user.ecs_profile, flag, False)