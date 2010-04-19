# -*- coding: utf-8 -*-

from ecs.core.views.utils import render, redirect_to_next_url
from ecs.feedback.models import Feedback


def feedback_input(request, type='idea'):
    fb_list = Feedback.objects.all().order_by('-pub_date')  # TODO restrict to feedbacktype iqpl

    page_size = 5
    items = len(fb_list)
    if items > 0:
        fb_page = 1  # TODO
        fb_pages = (items - 1) / page_size + 1
    else:
        fb_page = -1
        fb_pages = 0

    return render(request, 'input.html', {
        'type': type,
        'fb_list': fb_list,
        'fb_page': fb_page,
        'fb_pages': fb_pages,
    })

