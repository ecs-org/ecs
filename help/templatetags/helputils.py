# -*- coding: utf-8 -*-
from django.template import Library
from django.core.urlresolvers import reverse

from ecs.help.models import Page

register = Library()

@register.filter
def pagenav(page):
    return page.nav

@register.simple_tag
def help_url(slug):
    try:
        page = Page.objects.get(slug=slug)
        return reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk})
    except Page.DoesNotExist:
        return reverse('ecs.help.views.index')
