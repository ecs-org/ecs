from django import forms
from django.db.models import FieldDoesNotExist

def extend_field(model, name, **kwargs):
    field = None
    try:
        field = model._meta.get_field(name)
    except FieldDoesNotExist:
        for f in model._meta.many_to_many:
            if f.name == name:
                field = f
                break
        raise
    return field.formfield(**kwargs)


def mark_readonly(form):
    form.readonly = True
    for field in form.fields.itervalues():
        field.widget.attrs['readonly'] = 'readonly'
        field.widget.attrs['disabled'] = 'disabled'


class ReadonlyFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        super(ReadonlyFormMixin, self).__init__(*args, **kwargs)
        if self.readonly:
            mark_readonly(self)


class ReadonlyFormSetMixin(object):
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        extra = kwargs.pop('extra', None)
        if extra is not None:
            self.extra = extra
        super(ReadonlyFormSetMixin, self).__init__(*args, **kwargs)
        if self.readonly:
            for form in self.forms:
                mark_readonly(form)

