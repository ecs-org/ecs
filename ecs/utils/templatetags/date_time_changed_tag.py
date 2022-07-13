
from django import template
from django.conf import settings

register = template.Library()

def date_time_changed():
    return settings.ECS_CHANGED

register.simple_tag(date_time_changed)
