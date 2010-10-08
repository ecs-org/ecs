# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.feedback.models import Feedback
from ecs.utils import tracrpc

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
    rpc = tracrpc.TracRpc.from_dict(settings.FEEDBACK_CONFIG['RPC_CONFIG'])
    
     
    
    if request.method == 'POST' and request.POST.has_key('description'):
        description = request.POST['description']
        id = request.POST['fb_id']
        if id:
            # me2 vote (via GET)
            id = int(id)
            
            if id < 0:
                tid = id * -1
                add = False
            else:
                tid = id
                add = True
            
            ticket = rpc._get_ticket(tid)
            ticket = tracrpc.TracRpc.pad_ticket_w_emptystrings(ticket, settings.FEEDBACK_CONFIG['ticketfieldnames'])
            if ticket is not None:
                emails = ticket['cc'].split(',')
                in_cc = False
                for email in emails:
                    if user.email in email:
                        in_cc = True
                        emails.remove(email)
                if add:
                    #fb = Feedback.objects.get(id=id)
                    #fb.me_too_votes_add(user)
                    if not in_cc:
                        update_ticket = {'cc': "%s,%s" % (ticket['cc'], user.email)}
                        rpc._update_ticket(id, update_ticket, action='leave', comment='')
                else:
                    #fb = Feedback.objects.get(id=-id)
                    #fb.me_too_votes_remove(user)
                    update_ticket = {'cc':','.join(emails)}
                    rpc._update_ticket(int(id)*-1, update_ticket, action='leave', comment='')
            else:
                pass
            
        else:
            description_error = (description == '')
            if not (description_error):
                feedbacktype = type
                #pub_date = datetime.datetime.now()
                #feedback = Feedback(id=None, feedbacktype=feedbacktype, description=description, origin=origin, pub_date=pub_date, user=user)
                #feedback.save()
                if settings.FEEDBACK_CONFIG['create_trac_tickets'] == True:
                    tdict = {'feedbacktype': feedbacktype, 'description': description, 'origin': origin, 'creatoremail': user.email}
                    success, result = Feedback._create_trac_ticket_from_dict(tdict)
                
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
        print ""
        print "get_me2(fb) is DEPRECATED "
        if fb.user.id == user.id:
            return 'yours'
        elif fb.me_too_votes.filter(id=user.id).count() > 0:
            return 'u2'
        else:
            return 'me2'
    
    def get_count(fb):
        print ""
        print "get_count(fb) is DEPRECATED "
        return fb.me_too_votes.all().count()
       
       
   
    def get_me2_from_ticket(ticket):
        if user.email in ticket['ecsfeedback_creator']:
            return 'yours'
        emails = ticket['cc'].split(',')
        for email in emails:
            if user.email in email:
                 return 'u2'
        
        return 'me2'
        
    def get_me_too_count_from_ticket(ticket):
        emails = ticket['cc'].split(',')
        for email in emails:
            if email == '':
                emails.remove(email)
        count = len(emails)
        return count
    
    query_base = "order=id&col=id&col=summary&col=status&col=type&col=priority&col=milestone&col=component"
    #query = query_base + "&type=idea&type=question&type=problem&type=praise"
    query = query_base + "&type=%s" % m[type].lower()
    query += "&absoluteurl=%s" % origin
    #query = "errortest"
    results = None
    ticket_count = 0
    
    ticket_ids = rpc._safe_rpc(rpc.jsonrpc.ticket.query, query)
    if ticket_ids is not None:        
        mc = rpc.multicall()
        for tid in ticket_ids:
            mc.ticket.get(tid)
        results = rpc._safe_rpc(mc)

    if results is not None:
        ticket_count = len(results.results['result'])
        for result in results.results['result'][index:index+page_size]:
            ticket = rpc._get_ticket_from_rawticket(result['result'])
            ticket = tracrpc.TracRpc.pad_ticket_w_emptystrings(ticket, settings.FEEDBACK_CONFIG['ticketfieldnames'])
            index += 1
            
            list.append({
                'index': index,
                'id': ticket['id'],
                'description': ticket['summary'],
                'me2': get_me2_from_ticket(ticket),
                'count': get_me_too_count_from_ticket(ticket),
                'origin': origin
            })
        
#    for fb in Feedback.objects.order_by('-pub_date'):
#        print "ticket:",fb.description,'get_count(fb)',get_count(fb)
#        index = index + 1
#        list.append({
#            'index': index,
#            'id': fb.id,
#            'description': fb.description,
#            'me2': get_me2(fb),
#            'count': get_count(fb),
#        })

    # calculate number of pages
    #items = Feedback.objects.filter(feedbacktype=type).filter(origin=origin).count()
    items = ticket_count
    
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
    return render(request, 'feedback/main.html', {})

