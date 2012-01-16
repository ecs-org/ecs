
from django import template
from django.conf import settings

register = template.Library()

def userswitcher_enabled():
    return settings.ECS_USERSWITCHER

register.simple_tag(userswitcher_enabled)
