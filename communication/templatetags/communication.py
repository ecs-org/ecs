import datetime
from django.template import Library, Node, TemplateSyntaxError
from django.core.cache import cache
from ecs.communication.models import Message

register = Library()


class FetchMessagesNode(Node):
    def __init__(self, varname):
        super(FetchMessagesNode, self).__init__()
        self.varname = varname

    def render(self, context):
        user = context['request'].user
        cache_key = "ecs.communication:last_pull:%s" % user.pk
        last_pull = cache.get(cache_key)

        messages = Message.objects.filter(receiver=user, unread=True)
        if last_pull:
            messages = messages.filter(timestamp__gt=last_pull)

        cache.set(cache_key, datetime.datetime.now(), 7*24*3600)
        context[self.varname] = messages
        return u''

@register.tag
def fetch_messages(parser, token):
    try:
        name, as_, varname = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError('{% fetch_messages as VAR %} expected')
    return FetchMessagesNode(varname)



@register.filter
def closed_by(thread, user):
    if user == thread.sender:
        return thread.closed_by_sender
    elif user == thread.receiver:
        return thread.closed_by_receiver
    else:
        return None

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


