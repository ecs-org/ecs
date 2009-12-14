"""
Feedback Template Tags
======================
"""

from django.contrib.contenttypes.models import ContentType
from django import template

register = template.Library()

@register.inclusion_tag("feedback/feedbackform.html")
def feedback_form(object):
    return {
        "object" : object,
    }

@register.inclusion_tag("feedback/feedbackform_popup.html")
def feedback_form_popup(object):
    return {
        "object" : object,
    }

@register.inclusion_tag("feedback/feedbacksummary.html")
def feedback_summary(object):
    return {
        "object" : object,
        "comment_list" : comments,
    }
