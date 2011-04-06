# -*- coding: utf-8 -*-
from functools import wraps

from ecs.communication.models import Thread
from ecs.tasks.models import Task
from ecs.core.models import Submission
from ecs.users.utils import get_user
from ecs.utils.viewutils import render

def msg_fun(func):
    @wraps(func)
    def _inner(sender, receiver, *args, **kwargs):
        if isinstance(sender, basestring):
            sender = get_user(sender)
        if isinstance(receiver, basestring):
            receiver = get_user(receiver)
        if isinstance(kwargs['submission'], (basestring, int)):
            kwargs['submission'] = Submission.objects.get(pk=int(submission))
        if isinstance(kwargs['task'], (basestring, int)):
            kwargs['task'] = Task.objects.get(pk=int(task))

        args = [sender, receiver] + list(args)
        return func(*args, **kwargs)

    return _inner

@msg_fun
def send_message(sender, receiver, subject, text, submission=None, task=None):
    thread = Thread.objects.create(
        subject=subject,
        sender=sender, 
        receiver=receiver,
        submission=submission,
        task=task,
    )
    message = thread.add_message(sender, text=text)
    return thread

@msg_fun
def send_message_template(request, template, context, *args, **kwargs):
    context.setdefault('sender', sender)
    context.setdefault('receiver', receiver)
    context.setdefault('submission', submission)
    context.setdefault('task', task)
    kwargs['text'] = render(request, template, context)
    return send_message(*args, **kwargs)

