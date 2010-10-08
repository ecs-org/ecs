import traceback
import datetime
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage
from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.core.models import Submission
from ecs.tasks.models import Task
from ecs.communication.models import Message, Thread
from ecs.communication.forms import SendMessageForm, ReplyToMessageForm, ThreadDelegationForm
from ecs.tracking.decorators import tracking_hint

def send_message(request, submission_pk=None, reply_to_pk=None):
    submission, task, reply_to = None, None, None

    if submission_pk is not None:
        submission = get_object_or_404(Submission, pk=submission_pk)
    
    if reply_to_pk is not None:
        reply_to = get_object_or_404(Message, pk=reply_to_pk)
        thread = reply_to.thread
        form = ReplyToMessageForm(request.POST or None, initial={
            'subject': 'Re: %s' % thread.subject,
            'text': '%s schrieb:\n> %s' % (reply_to.sender, '\n> '.join(reply_to.text.split('\n')))
            
        }, instance = Message(thread=thread))
        submission = thread.submission
    else:
        form = SendMessageForm(request.POST or None)
        task_pk = request.GET.get('task')
        thread = None
        if task_pk is not None:
            task = get_object_or_404(Task, pk=task_pk)
            # FIXME: filter by contenttype
            submission = task.data

    if request.method == 'POST' and form.is_valid():
        if not thread:
            thread = Thread.objects.create(
                subject=form.cleaned_data['subject'],
                sender=request.user, 
                receiver=form.cleaned_data['receiver'],
                task=task,
                submission=submission,
            )

        message = thread.add_message(request.user, text=form.cleaned_data['text'])
        return redirect_to_next_url(request, reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': thread.pk}))

    return render(request, 'communication/send.html', {
        'submission': submission,
        'task': task,
        'form': form,
        'thread': thread,
    })

def read_thread(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    msg = thread.last_message 
    if msg.unread and msg.receiver == request.user:
        msg.unread = False
        msg.save()
    qs = thread.messages.order_by('-timestamp')
    try:
        page_num = int(request.GET.get('p', 1))
    except ValueError:
        page_num = 1
    paginator = Paginator(qs, 1000) # FIXME: do we really need pagination?
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page_num = paginator.num_pages
        page = paginator.page(page_num)

    return render(request, 'communication/read.html', {
        'thread': thread,
        'page': page,
    })

def bump_message(request, message_pk=None):
    if message_pk is not None:
        reply_to = get_object_or_404(Message, pk=message_pk)
        thread = reply_to.thread
        form = ReplyToMessageForm(request.POST or None, initial={
            'subject': 'Re: %s' % thread.subject,
            'text': '%s schrieb:\n> %s' % (reply_to.sender, '\n> '.join(reply_to.text.split('\n')))
            
        }, instance = Message(thread=thread))
        submission = thread.submission

    message = get_object_or_404(Message.objects.by_user(request.user), pk=message_pk)
    message.thread.add_message(request.user, message.text)
    return HttpResponse('OK')

def close_thread(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    thread.mark_closed_for_user(request.user)
    return HttpResponse('OK')
    
def delegate_thread(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    form = ThreadDelegationForm(request.POST or None)
    if form.is_valid():
        message = thread.add_message(request.user, text=form.cleaned_data['text'])
        thread.delegate(request.user, form.cleaned_data['to'])

        return render(request, 'communication/delegate_thread_response.html', {
            'to': form.cleaned_data['to'],
            'thread': thread,
        })
    return render(request, 'communication/delegate_thread.html', {
        'thread': thread,
        'form': form,
    })
    
@tracking_hint(exclude=True)
def incoming_message_widget(request):
    qs = Thread.objects.incoming(request.user).open(request.user)
    submission_pk = request.GET.get('submission', None)
    if submission_pk:
        qs = qs.filter(submission__pk=submission_pk)
    return message_widget(request, 
        queryset=qs,
        template='communication/widgets/incoming_messages.inc',
        user_sort='last_message__sender__username',
        session_prefix='dashboard:incoming_messages',
        page_size=4,
        extra_context={
            'incoming': True
        }
    )

@tracking_hint(exclude=True)
def outgoing_message_widget(request):
    qs = Thread.objects.outgoing(request.user).open(request.user)
    submission_pk = request.GET.get('submission', None)
    if submission_pk:
        qs = qs.filter(submission__pk=submission_pk)
    return message_widget(request, 
        queryset=qs,
        template='communication/widgets/outgoing_messages.inc',
        user_sort='last_message__receiver__username',
        session_prefix='dashboard:outgoing_messages',
        page_size=4,
    )

@tracking_hint(exclude=True)
def communication_overview_widget(request, submission_pk=None):
    return render(request, 'communication/widgets/overview.inc', {
        'threads': Thread.objects.filter(submission__pk=submission_pk),
    })

def message_widget(request, queryset=None, template='communication/widgets/messages.inc', user_sort=None, session_prefix='messages', extra_context=None, page_size=4):
    queryset = queryset.select_related('thread')

    sort_session_key = '%s:sort' % session_prefix
    sort = request.GET.get('sort', request.session.get(sort_session_key, '-timestamp'))
    
    if sort:
        if not sort in ('timestamp', '-timestamp', 'user', '-user', 'thread__submission', '-thread__submission'):
            sort = None
        if sort and sort.endswith('user'):
            if user_sort:
                queryset = queryset.order_by(sort.replace('user', user_sort))
            else:
                sort = None
    
    request.session[sort_session_key] = sort

    page_session_key = 'dashboard:%s:page' % session_prefix
    try:
        page_num = int(request.GET.get('p', request.session.get(page_session_key, 1)))
    except ValueError:
        page_num = 1
    paginator = Paginator(queryset, page_size)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page_num = paginator.num_pages
        page = paginator.page(page_num)
    request.session[page_session_key] = page_num

    context = {
        'page': page,
        'sort': sort,
    }
    if extra_context:
        context.update(extra_context)
    return render(request, template, context)

def inbox(request):
    return message_widget(request, 
        template='communication/inbox.html',
        queryset=Thread.objects.incoming(request.user).order_by('-last_message__timestamp'),
        session_prefix='messages:inbox',
        user_sort='sender__username',
        page_size=3,
    )

def outbox(request):
    return message_widget(request, 
        template='communication/outbox.html',
        queryset=Thread.objects.outgoing(request.user).order_by('-last_message__timestamp'),
        session_prefix='messages:outbox',
        user_sort='receiver__username',
        page_size=3,
    )
