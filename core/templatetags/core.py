from django.template import Library

from ecs.core.paper_forms import get_number_for_fieldname

register = Library()

register.filter('getattr', lambda obj, name: getattr(obj, str(name)))
register.filter('getitem', lambda obj, name: obj[name])
register.filter('type_name', lambda obj: type(obj).__name__)

@register.filter
def paperform_number(field_name):
    try:
        return get_number_for_fieldname(field_name)
    except KeyError:
        return None
