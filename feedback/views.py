# -*- coding: utf-8 -*-

from ecs.core.views.utils import render, redirect_to_next_url

def feedback_input(request):
    return render(request, 'input.html', {
    })

