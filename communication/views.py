# -*- coding: utf-8 -*-
import traceback
import datetime
import os

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.core.models import Submission
from ecs.tasks.models import Task
from ecs.communication.models import Message, Thread
from ecs.communication.forms import SendMessageForm, ReplyToMessageForm, ThreadDelegationForm
from ecs.tracking.decorators import tracking_hint
from ecs.communication.forms import ThreadListFilterForm

def send_message(request, submission_pk=None, reply_to_pk=None, to_user_pk=None, bump_message_pk=None):
    submission, task, reply_to, to_user = None, None, None, None

    if submission_pk is not None:
        submission = get_object_or_404(Submission, pk=submission_pk)
    
    if to_user_pk is not None:
        to_user = get_object_or_404(User, pk=to_user_pk)
    
    if reply_to_pk is not None:
        reply_to = get_object_or_404(Message, pk=reply_to_pk)
        thread = reply_to.thread
        form = ReplyToMessageForm(request.POST or None, initial={
            'text': _('%(sender)s schrieb:%(linesep)s> %(text)s' % {'linesep':os.linesep, 'sender': reply_to.sender, 'text': '\n> '.join(reply_to.text.split('\n'))})
            
        }, instance = Message(thread=thread))
        submission = thread.submission
    elif bump_message_pk is not None:
        bump_message = get_object_or_404(Message, pk=bump_message_pk)
        thread = bump_message.thread
        form = ReplyToMessageForm(request.POST or None, initial={
            'text': bump_message.text
        }, instance = Message(thread=thread))
        to_user = bump_message.receiver
    else:
        task_pk = request.GET.get('task')
        if task_pk is not None:
            task = get_object_or_404(Task, pk=task_pk)
            submission = task.data.get_submission() or submission

        form = SendMessageForm(submission, request.user, request.POST or None)
        thread = None

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
        'to_user': to_user,
        'task': task,
        'form': form,
        'thread': thread,
        'bump': bump_message_pk is not None,
    })

def read_thread(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    msg = thread.last_message 
    if msg.unread and msg.receiver == request.user:
        msg.unread = False
        msg.save()
    return render(request, 'communication/read.html', {
        'thread': thread,
        'message_list': thread.messages.order_by('-timestamp'),
    })

def thread(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    msg = thread.last_message 
    if msg.unread and msg.receiver == request.user:
        msg.unread = False
        msg.save()

    def get_reply_text(msg):
        if msg.sender == request.user:  # bump
            return u'\n>' + u'\n>'.join(msg.text.splitlines())
        else:
            reply_text = _(u'{sender} schrieb:').format(sender=msg.sender)
            return reply_text + u'\n>' + u'\n>'.join(msg.text.splitlines())

    form = ReplyToMessageForm(request.POST or None, initial={'text': get_reply_text(msg)})

    if request.method == 'POST' and form.is_valid():
        msg = thread.add_message(request.user, text=form.cleaned_data['text'])
        form = ReplyToMessageForm(None, initial={'text': get_reply_text(msg)})

    return render(request, 'communication/thread.html', {
        'thread': thread,
        'message_list': thread.messages.order_by('timestamp'),
        'form': form,
    })

def close_thread(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    thread.mark_closed_for_user(request.user)
    return redirect_to_next_url(request, reverse('ecs.communication.views.outgoing_message_widget'))
    
def delegate_thread(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    form = ThreadDelegationForm(request.POST or None)
    if form.is_valid():
        thread.delegate(request.user, form.cleaned_data['to'])

        new_thread = Thread.objects.create(
            subject=_(u'Abgeben von: {0}').format(thread.subject),
            sender=request.user,
            receiver=form.cleaned_data['to'],
            task=thread.task,
            submission=thread.submission,
        )
        message = new_thread.add_message(request.user, text=form.cleaned_data['text'])

        return HttpResponseRedirect(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': new_thread.pk}))

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
        extra_context={
            'incoming': False
        }
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

def threads(request):
    usersettings = request.user.ecs_settings

    filter_defaults = {
        'incoming': 'on',
        'outgoing': 'on',
    }

    filterdict = request.POST or usersettings.communication_filter or filter_defaults
    filterform = ThreadListFilterForm(filterdict)
    filterform.is_valid() # force clean

    usersettings.communication_filter = filterform.cleaned_data
    usersettings.save()

    queryset = Thread.objects.none()
    if filterform.cleaned_data['incoming']:
        queryset |= Thread.objects.incoming(request.user)
    if filterform.cleaned_data['outgoing']:
        queryset |= Thread.objects.outgoing(request.user)

    return message_widget(request, 
        template='communication/threads.html',
        queryset=queryset.order_by('-last_message__timestamp'),
        session_prefix='messages:unified',
        user_sort='receiver__username',
        page_size=10,
        extra_context={'filterform': filterform},
    )



