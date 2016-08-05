from django.template import Library, TemplateSyntaxError, Node

from ecs.scratchpad.models import ScratchPad

register = Library()

class ScratchpadNode(Node):
    def __init__(self, varname):
        super().__init__()
        self.varname = varname

    def render(self, context):
        try:
            context[self.varname] = ScratchPad.objects.get(
                owner=context['request'].user,
                submission=context.get('submission'),
            )
        except ScratchPad.DoesNotExist:
            context[self.varname] = None
        return ''

@register.tag
def get_scratchpad(parser, token):
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != 'as':
        raise TemplateSyntaxError('expected {% get_scratchpad as [var] %}')
    return ScratchpadNode(bits[2])
