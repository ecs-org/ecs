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
register.filter('startwith', lambda obj, start: obj.startswith(substr))
register.filter('endswith', lambda obj, end: obj.endswith(end))

@register.filter
def get_field_info(formfield):
    if formfield:
        return paper_forms.get_field_info(model=formfield.form._meta.model, name=formfield.name)
    else:
        return None
        
@register.filter
def simple_timedelta_format(td):
    if not td.seconds:
        return "0"
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    result = []
    if hours:
        result.append("%sh" % hours)
    if minutes:
        result.append("%smin" % minutes)
    if seconds:
        result.append("%ss" % seconds)
    return " ".join(result)

@register.filter
def empty_form(formset):
    # FIXME: replace with formset.empty_form when we switch to django 1.2
    defaults = {
        'auto_id': formset.auto_id,
        'prefix': formset.add_prefix('__prefix__'),
        'empty_permitted': True,
    }
    if formset.data or formset.files:
        defaults['data'] = formset.data
        defaults['files'] = formset.files
    defaults.update(kwargs)
    form = formset.form(**defaults)
    formset.add_fields(form, None)
    return form
