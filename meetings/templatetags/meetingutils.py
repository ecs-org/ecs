# -*- coding: utf-8 -*-
from datetime import timedelta

from django import template

register = template.Library()

@register.filter
def datetimeround(d, res):
    if res > 0:
        if d.minute % res > 0:
            d += timedelta(minutes=res-d.minute%res)
    else:
        res = 0 - res
        d -= timedelta(minutes=d.minute%res)
    return d
