from django import forms
from django.db.models import FieldDoesNotExist


def mark_readonly(form):
    form.readonly = True
    for field in form.fields.itervalues():
        field.widget.attrs['readonly'] = 'readonly'
        field.widget.attrs['disabled'] = 'disabled'


class ReadonlyFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        self.complete_task = kwargs.pop('complete_task', False)
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

