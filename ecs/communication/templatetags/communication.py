from django.template import Library, Node, TemplateSyntaxError
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


class UnreadMsgCountNode(Node):
    def __init__(self, varname):
        super().__init__()
        self.varname = varname

    def render(self, context):
        user = context['user']
        count = Thread.objects.by_user(user).annotate(
            unread_count=Sum(
                Case(
                    When(messages__receiver=user, messages__unread=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).filter(unread_count__gt=0).count()

        if self.varname:
            context[self.varname] = count
            return ''
        else:
            return count


@register.tag
def unread_msg_count(parser, token):
    bits = token.split_contents()
    if len(bits) == 1:
        kw_, = bits
        varname = None
    elif len(bits) == 3 and bits[1] == 'as':
        kw_, as_, varname = bits
    else:
        raise TemplateSyntaxError('{% unread_msg_count [as VAR] %}')

    return UnreadMsgCountNode(varname)
