import datetime
from django.template import Library, Node, TemplateSyntaxError
from django.core.cache import cache
from ecs.communication.models import Message
from ecs.users.models import UserProfile

register = Library()

def _username_for_message(message, attr, user):
    target_user = getattr(message, attr, None)
    # FIXME: those try/except blocks should go away when we can assume that every user has a profile
    try:
        mask = target_user.get_profile().internal
    except UserProfile.DoesNotExist:
        mask = False
    try:
        if user.get_profile().internal:
            mask = False
    except UserProfile.DoesNotExist:
        pass
    if mask:
        groups = target_user.groups.all()
        if message.thread.task:
            groups &= message.task.task_type.groups.all()
        if len(groups) == 1:
            return groups[0].name
    return target_user.username

@register.filter
def sender_name(message, user):
    return _username_for_message(message, 'sender', user)
    
@register.filter
def receiver_name(message, user):
    return _username_for_message(message, 'receiver', user)

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
    
