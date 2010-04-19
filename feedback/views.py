# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from ecs.core.views.utils import render, redirect_to_next_url
from ecs.feedback.models import Feedback
import datetime


def feedback_input(request, type='i'):
    m = dict(Feedback.FEEDBACK_TYPES)
    if not m.has_key(type):
        return HttpResponse("Error: unknown feedback type '%s'!" % type)

    if request.method == 'POST':
        description = request.POST['description']
        summary = request.POST['summary']
        feedbacktype = type
        origin = 'TODO'
        question = 'WTF'
        pub_date = datetime.datetime.now()
        feedback = Feedback(id=None, feedbacktype=feedbacktype, summary=summary, description=description, origin=origin, question=question, pub_date=pub_date)
        feedback.save()
        return render(request, 'thanks.html', {
           'type': type,
           'description': description,
           'summary': summary,
        })
 
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

