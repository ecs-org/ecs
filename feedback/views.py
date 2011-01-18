# -*- coding: utf-8 -*-

import datetime
import random
import types

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.feedback.models import Feedback
from ecs.utils import tracrpc

def feedback_input(request, type='i', page=1, origin='TODO'):

    def get_me2(email, fb):
        if email in fb.creator_email:
            return 'yours'
        elif email in fb.me_too_emails_string:
            return 'u2'
        else:
            return 'me2'
    
    def get_count(fb):
        count = len(fb.me_too_emails)
        #creator_email is always in cc but shouldn't be counted here
        #this count is only for all others but not the creator
        count -= 1 if count > 0 else 0
        return count

    if not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in!")
    else:
        user = request.user
        if user is None:
            return HttpResponse("Error: user is none!")
        
        if hasattr(request, "original_user"): # get the original user if the userswitcher is active
            user = request.original_user
            
    m = dict(Feedback.FEEDBACK_TYPES)
    if not m.has_key(type):
        return HttpResponse("Error: unknown feedback type '%s'!" % type)

    feedback_error = False
    summary = description = ''
    rpc = tracrpc.TracRpc.from_dict(settings.FEEDBACK_CONFIG['RPC_CONFIG'])
    
    if request.method == 'POST' and request.POST.has_key('summary'):
        summary = request.POST['summary']
        description = request.POST['description'] if request.POST.has_key('description') else ""
        id = request.POST['fb_id']
        
        if id: # me2 vote
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
            feedback_error = not summary
            if not (feedback_error):
                ticket = {'type': Feedback.ftdict[type].lower(), 
                          'summary': summary, 
                          'component': 'feedback',
                          'description': description,
                          'absoluteurl': origin,
                          'ecsfeedback_creator': user.email}
                ticket = tracrpc.TracRpc.pad_ticket_w_emptystrings(ticket, settings.FEEDBACK_CONFIG['ticketfieldnames'])
                feedback = Feedback.init_from_dict(ticket)
                feedback.save()
                
                return render(request, 'feedback/thanks.html', {
                    'type': type,
                    'summary': summary,
                    'description': description,
                })

    try:
        page = int(page)
        if page < 1:
            raise ValueError("page is 1 based (why?)")
    except ValueError:
        return HttpResponse("Error: invalid parameter page = '%s'!" % page)
    page_size = 3  # TODO: use django.core.paginator.Paginator (FMD3)
    
    types = [ x[0] for x in Feedback.FEEDBACK_TYPES ]
    # create display list from database fb records
    list = []
    index = (page - 1) * page_size;
    
    overall_count, fb_list = Feedback.query(limit_from=index, limit_to=(index+page_size), feedbacktype=type, origin=origin)
    
    for fb in fb_list:
        index += 1            
        list.append({
            'index': index,
            'id': fb.trac_ticket_id,
            'summary': fb.summary,
            'description': fb.description,
            'me2': get_me2(user.email, fb),
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
        'summary': summary,
        'description': description,
        'feedback_error': feedback_error,
    })


