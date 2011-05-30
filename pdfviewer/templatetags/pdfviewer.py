from django.template import Library, TemplateSyntaxError, Node
from django.utils import simplejson
from django.utils.safestring import mark_safe

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
    
@register.filter
def images(document):
    data = simplejson.dumps(document.get_pages_list())
    return mark_safe(data)

@register.filter
def annotations_for_user(document, user):
    annotations = list(document.annotations.filter(user=user).values(
        'pk', 'page_number', 'x', 'y', 'width', 'height', 'text', 'author__id', 'author__username'))
    data = simplejson.dumps(annotations)
    return mark_safe(data)

@register.filter
def is_ready(document):
    return document.status == 'ready'

