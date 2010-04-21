# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
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

    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user

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
        id = request.POST['fb_id']
        if id:
            # me2 vote (via GET)
            fb = Feedback.objects.get(id=id)
            fb.me_too_votes.add(user)
        else:
            description_error = (description == '')
            summary_error = (summary == '')
            if not (description_error or summary_error):
                feedbacktype = type
                pub_date = datetime.datetime.now()
                feedback = Feedback(id=None, feedbacktype=feedbacktype, summary=summary, description=description, origin=origin, pub_date=pub_date, user=user)
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

    def get_me2(fb):
        if fb.user.id == user.id:
            return 'yours'
        elif len(fb.me_too_votes.filter(id=user.id)) > 0:
            return 'u2'
        else:
            return 'me2'

    def get_count(fb):
        return len(fb.me_too_votes.all())

    for fb in Feedback.objects.filter(feedbacktype=type).filter(origin=origin).order_by('-pub_date')[index:index+page_size]:
        index = index + 1
        list.append({
            'index': index,
            'id': fb.id,
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

