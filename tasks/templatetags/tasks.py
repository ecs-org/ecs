import datetime
from django.template import Library, Node, TemplateSyntaxError
from django.core.cache import cache
from ecs.tasks.models import Task

register = Library()

class FetchTasksNode(Node):
    def __init__(self, varname):
        super(FetchTasksNode, self).__init__()
        self.varname = varname

    def render(self, context):
        user = context['request'].user
        cache_key = "ecs.tasks:last_pull:%s" % user.pk
        last_pull = cache.get(cache_key)
        if last_pull:
            tasks = Task.objects.filter(assigned_to=user, accepted=False, assigned_at__gt=last_pull)
        else:
            tasks = Task.objects.none()
        cache.set(cache_key, datetime.datetime.now(), 7*24*3600)
        context[self.varname] = tasks
        return u''

@register.tag
def fetch_tasks(parser, token):
    try:
        name, as_, varname = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError('{% fetch_tasks as VAR %} expected')
    return FetchTasksNode(varname)