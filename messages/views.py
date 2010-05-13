from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Q
from ecs.core.views.utils import render, redirect_to_next_url
from ecs.core.models import Submission
from ecs.tasks.models import Task
from ecs.messages.models import Message
from ecs.messages.forms import SendMessageForm, ReplyToMessageForm

def send_message(request, submission_pk=None, reply_to_pk=None):
    submission, task, reply_to = None, None, None

    if submission_pk is not None:
        submission = get_object_or_404(Submission, pk=submission_pk)
    
    if reply_to_pk is not None:
        reply_to = get_object_or_404(Message, pk=reply_to_pk)
        form = ReplyToMessageForm(request.POST or None, initial={
            'subject': 'Re: %s' % reply_to.subject,
            'text': '%s schrieb:\n> %s' % (reply_to.sender, '\n> '.join(reply_to.text.split('\n')))
        })
        submission = reply_to.submission
    else:
        form = SendMessageForm(request.POST or None)
        task_pk = request.GET.get('task')
        if task_pk is not None:
            task = get_object_or_404(Task, pk=task_pk)
            # FIXME: filter by contenttype
            submission = task.data

    if request.method == 'POST' and form.is_valid():
        message = form.save(commit=False)
        message.sender = request.user
        message.submission = submission
        message.reply_to = reply_to
        if reply_to:
            message.receiver = reply_to.sender
        message.save()
        return redirect_to_next_url(request, reverse('ecs.messages.views.outbox'))

    return render(request, 'messages/send.html', {
        'submission': submission,
        'task': task,
        'form': form,
    })
    
def inbox(request):
    return render(request, 'messages/inbox.html', {
        'message_list': Message.objects.select_related('sender', 'receiver').filter(receiver=request.user).order_by('-timestamp'),
    })

def outbox(request):
    return render(request, 'messages/outbox.html', {
        'message_list': Message.objects.select_related('sender', 'receiver').filter(sender=request.user).order_by('-timestamp'),
    })
    
def list_messages(request):
    return render(request, 'messages/list.html', {
        'message_list': Message.objects.select_related('sender', 'receiver').order_by('-timestamp'),
    })    

def read_message(request, message_pk=None):
    message = get_object_or_404(Message.objects.by_user(request.user), pk=message_pk)
    if message.unread and message.receiver == request.user:
        message.unread = False
        message.save()
    return render(request, 'messages/read.html', {
        'message': message,
    })
    