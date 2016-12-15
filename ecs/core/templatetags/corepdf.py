import base64

from django.template import Library, Node
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from ecs.core.models import AdvancedSettings


register = Library()


@register.filter
def checkbox(val):
    return mark_safe('<span class="checkbox">%s</span>' % (val and "X" or " "))
checkbox.is_safe = True

@register.filter
def yesno_checkboxes(val):
    return mark_safe('<span class="yesno">%s %s %s %s</span>' % (checkbox(val), _('yes'), checkbox(not val), _('no')))
yesno_checkboxes.is_safe = True


class SingleCellTableNode(Node):
    def __init__(self, class_name, nodelist):
        self.class_name = class_name
        self.nodelist = nodelist

    def render(self, context):
        return '<table class="%s"><tr><td>%s</td></tr></table>' % (self.class_name, self.nodelist.render(context))

#
@register.tag
def tcwrap(parser, token):
    _, class_name = token.split_contents()
    nodelist = parser.parse(('endtcwrap',))
    parser.delete_first_token()
    return SingleCellTableNode(class_name, nodelist)


@register.simple_tag
def print_logo_url():
    s = AdvancedSettings.objects.get()
    if not s.print_logo:
        return 'static:images/fallback_logo.png'
    return 'data:{};base64,{}'.format(s.print_logo_mimetype,
        base64.b64encode(s.print_logo).decode('ascii'))
