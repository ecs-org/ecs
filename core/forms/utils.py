from django import forms
from django.db.models import FieldDoesNotExist
from django.forms.models import model_to_dict

from ecs.core.forms.fields import ReadonlyTextInput, ReadonlyTextarea

def mark_readonly(form):
    form.readonly = True
    for field in form.fields.itervalues():
        if hasattr(field.widget, 'mark_readonly'):
            field.widget.mark_readonly()
        else:
            field.widget.attrs['readonly'] = 'readonly'
            field.widget.attrs['disabled'] = 'disabled'

class ReadonlyFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        self.related_task = kwargs.pop('related_task', None)
        self.reopen_task = kwargs.pop('reopen_task', None)
        super(ReadonlyFormMixin, self).__init__(*args, **kwargs)
        if self.readonly:
            mark_readonly(self)

class NewReadonlyFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        self.related_task = kwargs.pop('related_task', None)
        self.reopen_task = kwargs.pop('reopen_task', None)
        super(NewReadonlyFormMixin, self).__init__(*args, **kwargs)
        if self.readonly:
            for field in self.fields.itervalues():
                if isinstance(field.widget, (forms.TextInput,)):
                    attrs = field.widget.attrs.copy()
                    field.widget = ReadonlyTextInput(attrs=attrs)
                elif isinstance(field.widget, (forms.Textarea,)):
                    attrs = field.widget.attrs.copy()
                    if 'cols' in attrs: attrs.pop('cols')
                    if 'rows' in attrs: attrs.pop('rows')
                    field.widget = ReadonlyTextarea(attrs=attrs)
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

class NewReadonlyFormSetMixin(object):
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        extra = kwargs.pop('extra', None)
        if extra is not None:
            self.extra = extra
        super(NewReadonlyFormSetMixin, self).__init__(*args, **kwargs)
        if self.readonly:
            for form in self.forms:
                for field in form.fields.itervalues():
                    if isinstance(field.widget, (forms.TextInput,)):
                        field.widget = ReadonlyTextInput(attrs=field.widget.attrs)
                    elif isinstance(field.widget, (forms.Textarea,)):
                        field.widget = ReadonlyTextarea(attrs=field.widget.attrs)
                mark_readonly(form)

def submission_form_to_dict(sf):
    d = model_to_dict(sf)
    d['invoice_differs_from_sponsor'] = bool(sf.invoice_name)
    return d
