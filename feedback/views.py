# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from ecs.utils.viewutils import render, redirect_to_next_url
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
        if user is None:
            return HttpResponse("Error: user is none!")

    m = dict(Feedback.FEEDBACK_TYPES)
    if not m.has_key(type):
        return HttpResponse("Error: unknown feedback type '%s'!" % type)

    description = ''
    description_error = False

    if request.method == 'POST' and request.POST.has_key('description'):
        description = request.POST['description']
        id = request.POST['fb_id']
        if id:
            # me2 vote (via GET)
            id = int(id)
            if id > 0:
                fb = Feedback.objects.get(id=id)
                fb.me_too_votes.add(user)
            else:
                fb = Feedback.objects.get(id=-id)
                fb.me_too_votes.remove(user)
        else:
            description_error = (description == '')
            if not (description_error):
                feedbacktype = type
                pub_date = datetime.datetime.now()
                feedback = Feedback(id=None, feedbacktype=feedbacktype, description=description, origin=origin, pub_date=pub_date, user=user)
                feedback.save()
                return render(request, 'feedback/thanks.html', {
                    'type': type,
                    'description': description,
                })

    types = [ x[0] for x in Feedback.FEEDBACK_TYPES ]
 
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
        elif fb.me_too_votes.filter(id=user.id).count() > 0:
            return 'u2'
        else:
            return 'me2'

    def get_count(fb):
        return fb.me_too_votes.all().count()

    for fb in Feedback.objects.filter(feedbacktype=type).filter(origin=origin).order_by('-pub_date')[index:index+page_size]:
        index = index + 1
        list.append({
            'index': index,
            'id': fb.id,
            'description': fb.description,
            'me2': get_me2(fb),
            'count': get_count(fb),
        })

    # calculate number of pages
    items = Feedback.objects.filter(feedbacktype=type).filter(origin=origin).count()
    if items > 0:
        pages = (items - 1) / page_size + 1
        if page > pages:
            page = pages  # adjust
    else:
        pages = 0

    return render(request, 'feedback/input.html', {
        'type': type,
        'types': types,
        'list': list,
        'page': page,
        'items': items,
        'pages': pages,
        'origin': origin,
        'description': description,
        'description_error': description_error,
    })


def feedback_details(request, id=0):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
    fb = Feedback.objects.get(id=id)
    type = fb.feedbacktype
    me2_votes = fb.me_too_votes.all()
    return render(request, 'feedback/details.html', {
        'id': id,
        'fb': fb,
        'type': type,
        'me2_votes': me2_votes
    })


def feedback_origins(request):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user

    origins = [ x['origin'] for x in Feedback.objects.values('origin').distinct() ]
    types = [ x[0] for x in Feedback.FEEDBACK_TYPES ]
    list = [ { 'origin': origin, 'stats': [ (type, Feedback.objects.filter(feedbacktype=type, origin=origin).count()) for type in types ] } for origin in origins ]

    return render(request, 'feedback/origins.html', {
        'types': types,
        'list': list
    })


def feedback_main(request):
    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
    return render(request, 'feedback/main.html', {
    })
