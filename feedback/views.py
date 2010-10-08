# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.feedback.models import Feedback
from ecs.utils import tracrpc

import datetime
import random
import types


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
    rpc = tracrpc.TracRpc.from_dict(settings.FEEDBACK_CONFIG['RPC_CONFIG'])
    
    
    if request.method == 'POST' and request.POST.has_key('description'):
        description = request.POST['description']
        id = request.POST['fb_id']
        if id:
            # me2 vote (via GET)
            id = int(id)
            
            if id < 0:
                tid = id * -1
                fb = Feedback.get(tid)
                if fb is not None:
                    fb.me_too_votes_remove(user)
            else:
                tid = id
                fb = Feedback.get(tid)
                if fb is not None:
                    fb.me_too_votes_add(user)
            
            
        else:
            description_error = (description == '')
            if not (description_error):
                feedbacktype = type
                pub_date = datetime.datetime.now()
                
                
                #summary = description is on purpose
                ticket = {'type': Feedback.ftdict[feedbacktype].lower(), 'summary': description, 'absoluteurl': origin, 'ecsfeedback_creator': user.email}
                ticket = tracrpc.TracRpc.pad_ticket_w_emptystrings(ticket, settings.FEEDBACK_CONFIG['ticketfieldnames'])
                #ugly but works for now
                feedback = Feedback.init_from_dict(ticket)
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
        if user.email in fb.creator_email:
            return 'yours'
        elif user.email in fb.me_too_emails_string:
            return 'u2'
        else:
            return 'me2'
    
    def get_count(fb):
        return len(fb.me_too_emails)
       
    
    overall_count, fb_list = Feedback.query(limit_from=index, limit_to=(index+page_size), feedbacktype=type, origin=origin)
    
    for fb in fb_list:
        index += 1            
        list.append({
            'index': index,
            'id': fb.trac_ticket_id,
            'description': fb.description,
            'me2': get_me2(fb),
            'count': get_count(fb),
        })

    items = overall_count
    
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


