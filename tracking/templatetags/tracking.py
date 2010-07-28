from django.template import Library, TemplateSyntaxError, Node
from ecs.tracking.models import Request

register = Library()

class GetHistoryNode(Node):
    def __init__(self, var_name):
        self.var_name = var_name
    
    def render(self, context):
        request = context['request']
        context[self.var_name] = Request.objects.filter(user=request.user).order_by('-timestamp')[:5]
        return u""

@register.tag
def get_tracking_history(parser, token):
    """{% get_tracking_history as foo %}"""
    
    _, as_, var_name = token.split_contents()
    if as_ != 'as':
        raise TemplateSyntaxError('expected {% get_tracking_history as [varname] %}')
    return GetHistoryNode(var_name)