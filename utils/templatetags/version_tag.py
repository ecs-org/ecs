
from django import template
from django.conf import settings

register = template.Library()

def current_version():
    return settings.ECS_VERSION

register.simple_tag(current_version)
