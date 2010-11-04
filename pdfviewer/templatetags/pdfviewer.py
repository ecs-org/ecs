from django.template import Library, TemplateSyntaxError, Node

register = Library()

class AnnotationsNode(Node):
    def __init__(self, docvar, varname):
        self.docvar = docvar
        self.varname = varname

    def render(self, context):
        doc = self.docvar.resolve(context)
        print doc, doc.annotations.filter(user=context['request'].user).order_by('page_number', 'y')
        context[self.varname] = doc.annotations.filter(user=context['request'].user).order_by('page_number', 'y')
        return u""

@register.tag
def get_annotations(parser, token):
    bits = token.split_contents()
    if len(bits) != 5 or bits[1] != 'for' or bits[3] != 'as':
        raise TemplateSyntaxError("expected {% annotations for [doc] as [var] %}")
    return AnnotationsNode(parser.compile_filter(bits[2]), bits[4])
    
    
    