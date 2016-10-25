from django.template import Library
from django.db.models import Sum, Case, When, IntegerField

from ecs.communication.models import Thread


register = Library()


@register.filter
def starred_by(thread, user):
    if user.id == thread.sender_id:
        return thread.starred_by_sender
    elif user.id == thread.receiver_id:
        return thread.starred_by_receiver
    else:
        assert False


@register.filter
def remote(thread, user):
    if user == thread.sender:
        return thread.receiver
    elif user == thread.receiver:
        return thread.sender
    else:
        return None


@register.filter
def preview(message, chars):
    text = ' '.join(message.text.splitlines())
    if len(text) > chars:
        return text[:chars-3] + '...'
    else:
        return text


@register.simple_tag(takes_context=True)
def unread_msg_count(context):
    user = context['user']
    return Thread.objects.by_user(user).annotate(
        unread_count=Sum(
            Case(
                When(messages__receiver=user, messages__unread=True, then=1),
                default=0,
                output_field=IntegerField()
            )
        )
    ).filter(unread_count__gt=0).count()
