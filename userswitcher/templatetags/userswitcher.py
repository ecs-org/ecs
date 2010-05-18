from django.template import Library
from ecs.userswitcher.forms import UserSwitcherForm
from ecs.userswitcher import SESSION_KEY

register = Library()

@register.inclusion_tag('userswitcher/form.html', takes_context=True)
def userswitcher(context):
    request = context['request']
    #print request.session.get(SESSION_KEY)
    return {
        'form': UserSwitcherForm({'user': request.session.get(SESSION_KEY)}),
        'url': request.get_full_path(),
    }