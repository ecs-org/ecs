import re
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ecs.core.views.utils import render
from ecs.messages.models import Message, Thread
from ecs.tasks.models import Task
from django.core.paginator import Paginator, EmptyPage

def view_dashboard(request):
    tasks = tasks = Task.objects.filter(closed_at=None)
    accepted_tasks = tasks.filter(assigned_to=request.user, accepted=True)
    assigned_tasks = tasks.filter(assigned_to=request.user, accepted=False)
    open_tasks = tasks.filter(assigned_to=None)
    
    return render(request, 'dashboard/dashboard.html', {
        'accepted_tasks': accepted_tasks,
        'assigned_tasks': assigned_tasks,
        'open_tasks': open_tasks,
    })

def read_message(request, message_pk):
    message = get_object_or_404(Message.objects.by_user(request.user), pk=message_pk)
    if message.unread and message.receiver == request.user:
        message.unread = False
        message.save()
    return render(request, 'dashboard/read_message.html', {
        'message': message,
    })
    

def incoming_message_widget(request):
    return message_widget(request, 
        queryset=request.user.incoming_messages.filter(Q(thread__closed_by_receiver=False, thread__receiver=request.user) | Q(thread__closed_by_sender=False, thread__sender=request.user)), 
        template='dashboard/incoming_messages.inc',
        user_sort='sender__username',
        session_prefix='incoming_messages',
    )

def outgoing_message_widget(request):
    return message_widget(request, 
        queryset=request.user.outgoing_messages.filter(Q(thread__closed_by_receiver=False, thread__receiver=request.user) | Q(thread__closed_by_sender=False, thread__sender=request.user)), 
        template='dashboard/outgoing_messages.inc',
        user_sort='receiver__username',
        session_prefix='outgoing_messages',
    )

def message_widget(request, queryset=None, template='dashboard/messages.inc', user_sort=None, session_prefix='messages'):
    queryset = queryset.select_related('thread')

    sort_session_key = 'dashboard:%s:sort' % session_prefix
    sort = request.GET.get('sort', request.session.get(sort_session_key, '-timestamp'))
    if sort:
        if not sort in ('timestamp', '-timestamp', 'user', '-user'):
            sort = None
        if sort:
            queryset = queryset.order_by(sort.replace('user', user_sort))
    request.session[sort_session_key] = sort
    
    page_session_key = 'dashboard:%s:page' % session_prefix
    try:
        page_num = int(request.GET.get('p', request.session.get(page_session_key, 1)))
    except ValueError:
        page_num = 1
    paginator = Paginator(queryset, 4)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page_num = paginator.num_pages
        page = paginator.page(page_num)
    request.session[page_session_key] = page_num

    return render(request, template, {
        'page': page,
        'sort': sort,
    })
    