from django.template import Library

from ecs.core import paper_forms

register = Library()

register.filter('getattr', lambda obj, name: getattr(obj, str(name)))
register.filter('getitem', lambda obj, name: obj[name])
register.filter('type_name', lambda obj: type(obj).__name__)

@register.filter
def get_field_info(formfield):
    return paper_forms.get_field_info(model=formfield.form._meta.model, name=formfield.name)
