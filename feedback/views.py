# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from ecs.core.views.utils import render, redirect_to_next_url
from ecs.feedback.models import Feedback

import datetime
import random


def is_int(x):
    try:
        i = int(x)
        return True
    except:
        return False
  

def feedback_input(request, type='i', page=1):
    m = dict(Feedback.FEEDBACK_TYPES)
    if not m.has_key(type):
        return HttpResponse("Error: unknown feedback type '%s'!" % type)

    if request.method == 'POST':
        description = request.POST['description']
        summary = request.POST['summary']
        feedbacktype = type
        origin = 'TODO'
        question = 'WTF?!'
        pub_date = datetime.datetime.now()
        feedback = Feedback(id=None, feedbacktype=feedbacktype, summary=summary, description=description, origin=origin, question=question, pub_date=pub_date)
        feedback.save()
        return render(request, 'thanks.html', {
           'type': type,
           'description': description,
           'summary': summary,
        })

    types = m.keys()
 
    if not is_int(page) or page < 1:
        return HttpResponse("Error: invalid parameter page = '%s'!" % page)

    list = []
    index = 0;

    def get_me2():
        r = random.randint(0, 2)
        if r == 0:
            return 'yours'
        elif r == 1:
            return 'u2'
        else:
            return 'me2'

    for fb in Feedback.objects.all().order_by('-pub_date'):  # TODO restrict to type
        list.append({ 'index': index + 1, 'summary': fb.summary, 'description': fb.description, 'me2': get_me2() })
        list.append({ 'index': index + 2, 'summary': fb.summary, 'description': fb.description, 'me2': get_me2() })
        list.append({ 'index': index + 3, 'summary': fb.summary, 'description': fb.description, 'me2': get_me2() })
        list.append({ 'index': index + 4, 'summary': fb.summary, 'description': fb.description, 'me2': get_me2() })
        list.append({ 'index': index + 5, 'summary': fb.summary, 'description': fb.description, 'me2': get_me2() })
        list.append({ 'index': index + 6, 'summary': fb.summary, 'description': fb.description, 'me2': get_me2() })
        index = index + 6

    page_size = 5  # TODO emphasize parameter
    items = len(list)
    if items > 0:
        pages = (items - 1) / page_size + 1
        if page > pages:
            page = pages  # adjust
    else:
        pages = 0

    return render(request, 'input.html', {
        'type': type,
        'types': types,
        'list': list,
        'page': page,
        'pages': pages,
    })

