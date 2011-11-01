# -*- coding: utf-8 -*-
from functools import wraps

from django.template import RequestContext, Context, loader, Template
from django.conf import settings

from ecs.communication.models import Thread
from ecs.users.utils import get_user


def msg_fun(func):
    @wraps(func)
    def _inner(sender, receiver, *args, **kwargs):
        # import here to prevent circular imports
        from ecs.tasks.models import Task
        from ecs.core.models import Submission

        submission = kwargs.get('submission', None)
        task = kwargs.get('task', None)
        if isinstance(sender, basestring):
            sender = get_user(sender)
        if isinstance(receiver, basestring):
            receiver = get_user(receiver)
        kwargs['submission'] = Submission.objects.get(pk=int(submission)) if isinstance(submission, (basestring, int)) else submission
        kwargs['task'] = Task.objects.get(pk=int(task)) if isinstance(task, (basestring, int)) else task

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

def send_system_message(*args, **kwargs):
    return send_message(get_user('root@example.org'), *args, **kwargs)

@msg_fun
def send_message_template(sender, receiver, subject, template, context, *args, **kwargs):
    request = kwargs.get('request')
    if context is None:
        context = {}

    context.setdefault('sender', sender)
    context.setdefault('receiver', receiver)
    context.setdefault('submission', kwargs.get('submission'))
    context.setdefault('task', kwargs.get('task'))
    context.setdefault('ABSOLUTE_URL_PREFIX', settings.ABSOLUTE_URL_PREFIX)

    if isinstance(template, (tuple, list)):
        template = loader.select_template(template)
    if not isinstance(template, Template):
        template = loader.get_template(template)

    if request:
        text = template.render(RequestContext(request, context))
    else:
        text = template.render(Context(context))

    return send_message(sender, receiver, subject, text, *args, **kwargs)

def send_system_message_template(*args, **kwargs):
    return send_message_template(get_user('root@example.org'), *args, **kwargs)

