from functools import wraps

from django.template import loader
from django.conf import settings

from ecs.communication.models import Thread
from ecs.users.utils import get_user, get_office_user


def msg_fun(func):
    @wraps(func)
    def _inner(sender, receiver, *args, **kwargs):
        # import here to prevent circular imports
        from ecs.core.models import Submission

        submission = kwargs.get('submission', None)
        if isinstance(sender, str):
            sender = get_user(sender)
        if isinstance(receiver, str):
            receiver = get_user(receiver)
        kwargs['submission'] = Submission.objects.get(pk=int(submission)) if isinstance(submission, (str, int)) else submission

        args = [sender, receiver] + list(args)
        return func(*args, **kwargs)

    return _inner


@msg_fun
def send_message(sender, receiver, subject, text, submission=None, reply_receiver=None,
    rawmsg=None, outgoing_msgid=None, incoming_msgid=None, in_reply_to=None, creator=None):

    thread = Thread.objects.create(
        subject=subject,
        sender=sender,
        receiver=receiver,
        submission=submission,
    )
    if str(sender.email) == 'root@system.local':
        creator = 'auto-self'
        if not reply_receiver:
            reply_receiver = get_office_user(submission=submission)

    thread.add_message(sender, text,
        reply_receiver=reply_receiver, rawmsg=rawmsg,
        outgoing_msgid=outgoing_msgid, incoming_msgid=incoming_msgid,
        in_reply_to=in_reply_to, creator=creator)
    return thread


@msg_fun
def send_message_template(sender, receiver, subject, template, context, *args, **kwargs):
    request = kwargs.get('request')
    if context is None:
        context = {}
    else:
        context = context.copy()

    context.setdefault('sender', sender)
    context.setdefault('receiver', receiver)
    context.setdefault('submission', kwargs.get('submission'))
    context.setdefault('ABSOLUTE_URL_PREFIX', settings.ABSOLUTE_URL_PREFIX)

    if isinstance(template, (tuple, list)):
        template = loader.select_template(template)
    if not hasattr(template, 'render'):
        template = loader.get_template(template)

    text = template.render(context, request)

    return send_message(sender, receiver, subject, text, *args, **kwargs)


def send_system_message_template(*args, **kwargs):
    return send_message_template(get_user('root@system.local'), *args, **kwargs)
