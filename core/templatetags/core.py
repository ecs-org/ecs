from django.template import Library

from ecs.core import paper_forms

register = Library()

def getitem(obj, name):
    try:
        return obj[name]
    except KeyError:
        return None

register.filter('getattr', lambda obj, name: getattr(obj, str(name)))
register.filter('getitem', getitem)
register.filter('type_name', lambda obj: type(obj).__name__)

@register.filter
def get_field_info(formfield):
    if formfield:
        return paper_forms.get_field_info(model=formfield.form._meta.model, name=formfield.name)
    else:
        return None
