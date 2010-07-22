from django.template import Library, Node
from django.template.defaulttags import URLNode, url

from ecs.utils.hashauth import sign_url

register = Library()

class HashURLNode(URLNode):
    def render(self, context):
        url = super(HashURLNode, self).render(context)
        if self.asvar:
            context[self.asvar] = sign_url(context[self.asvar])
            return u""
        else:
            return sign_url(url)

@register.tag
def hashurl(parser, token):
    urlnode = url(parser, token)
    urlnode.__class__ = HashURLNode
    return urlnode