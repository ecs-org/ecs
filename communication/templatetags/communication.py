import datetime
from django.template import Library, Node, TemplateSyntaxError
from django.core.cache import cache
from ecs.communication.models import Message
from ecs.users.models import UserProfile

register = Library()


class FetchMessagesNode(Node):
    def __init__(self, varname):
        super(FetchMessagesNode, self).__init__()
        self.varname = varname

    def render(self, context):
        user = context['request'].user
        cache_key = "ecs.communication:last_pull:%s" % user.pk
        last_pull = cache.get(cache_key)
        if last_pull:
            messages = Message.objects.filter(receiver=user, timestamp__gt=last_pull)
        else:
            messages = Message.objects.filter(receiver=user, unread=True)
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
    
