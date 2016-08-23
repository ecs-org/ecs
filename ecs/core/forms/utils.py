from django import forms
from django.forms.models import model_to_dict

from ecs.core.forms.fields import ReadonlyTextInput, ReadonlyTextarea

def mark_readonly(form):
    form.readonly = True
    for field in form.fields.values():
        if hasattr(field.widget, 'mark_readonly'):
            field.widget.mark_readonly()
        else:
            field.widget.attrs['readonly'] = 'readonly'
            field.widget.attrs['disabled'] = 'disabled'

class ReadonlyFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        self.reopen_task = kwargs.pop('reopen_task', None)
        super().__init__(*args, **kwargs)
        if self.readonly:
            for field in self.fields.values():
                if isinstance(field.widget, forms.TextInput):
                    attrs = field.widget.attrs.copy()
                    field.widget = ReadonlyTextInput(attrs=attrs)
                elif isinstance(field.widget, forms.Textarea):
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
        super().__init__(*args, **kwargs)
        if self.readonly:
            for form in self.forms:
                for field in form.fields.values():
                    if isinstance(field.widget, forms.TextInput):
                        field.widget = ReadonlyTextInput(attrs=field.widget.attrs)
                    elif isinstance(field.widget, forms.Textarea):
                        field.widget = ReadonlyTextarea(attrs=field.widget.attrs)
                mark_readonly(form)

def submission_form_to_dict(sf):
    d = model_to_dict(sf)
    d['invoice_differs_from_sponsor'] = bool(sf.invoice_name)
    d['subject_females_childbearing'] = str((
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ).index((sf.subject_females, sf.subject_childbearing)))
    return d
