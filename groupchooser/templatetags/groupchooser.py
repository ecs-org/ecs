from django.template import Library
from ecs.groupchooser.forms import GroupChooserForm

register = Library()

@register.inclusion_tag('groupchooser/form.html', takes_context=True)
def groupchooser(context):
    request = context['request']
    #print request.session.get('groupchooser-data')
    return {
        'form': GroupChooserForm({'group': request.session.get('groupchooser-group_pk')}),
        'url': request.get_full_path(),
    }