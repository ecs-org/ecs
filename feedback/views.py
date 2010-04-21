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
  

def feedback_input(request, type='i', page=1, origin='TODO'):
    m = dict(Feedback.FEEDBACK_TYPES)
    if not m.has_key(type):
        return HttpResponse("Error: unknown feedback type '%s'!" % type)

    summary = ''
    summary_error = False
    description = ''
    description_error = False

    if request.method == 'POST' and request.POST.has_key('description'):
        description = request.POST['description']
        summary = request.POST['summary']
        description_error = (description == '')
        summary_error = (summary == '')
        if not (description_error or summary_error):
            feedbacktype = type
            question = 'WTF?!'
            pub_date = datetime.datetime.now()
            feedback = Feedback(id=None, feedbacktype=feedbacktype, summary=summary, description=description, origin=origin, question=question, pub_date=pub_date)
            feedback.save()
            return render(request, 'thanks.html', {
                'type': type,
                'description': description,
                'summary': summary,
            })

    types = []
    for t, _ in Feedback.FEEDBACK_TYPES:
        types.append(t)
 
    if not is_int(page) or page < 1:
        return HttpResponse("Error: invalid parameter page = '%s'!" % page)
    page = int(page)

    page_size = 4  # TODO emphasize parameter

    # create display list from database fb records
    list = []
    index = (page - 1) * page_size;

    def get_me2_random(fb):
        r = random.randint(0, 2)
        if r == 0:
            return 'yours'
        elif r == 1:
            return 'u2'
        else:
            return 'me2'
    def get_me2(fb):
        # TODO
        # yours: fb.user == user
        # u2: fb.user != user and user in fb.me2votes
        # me2: fb.user != user and not(user in fb.me2votes)
        return get_me2_random(fb)

    def get_count_random(fb):
        return random.randint(0, 3)
    def get_count(fb):
        # TODO
        # count = len(fb.me2votes)
        return get_count_random(fb)

    for fb in Feedback.objects.filter(feedbacktype=type).filter(origin=origin).order_by('-pub_date')[index:index+page_size]:
        index = index + 1
        list.append({
            'index': index,
            'summary': fb.summary,
            'description': fb.description,
            'me2': get_me2(fb),
            'count': get_count(fb),
        })

    # calculate number of pages
    items = len(Feedback.objects.filter(feedbacktype=type).filter(origin=origin))
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
        'items': items,
        'pages': pages,
        'origin': origin,
        'summary': summary,
        'summary_error': summary_error,
        'description': description,
        'description_error': description_error,
    })

