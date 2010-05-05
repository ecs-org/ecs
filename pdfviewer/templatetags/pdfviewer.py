# encoding: utf-8

from django import template

register = template.Library()


# work around for pre Django 1.2

@register.filter
def less(x, y):
    return x < y

@register.filter
def greater(x, y):
    return x > y
