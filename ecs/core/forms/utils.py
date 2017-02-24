from django import forms
from django.forms.models import model_to_dict
from django.utils.translation import ugettext as _


def mark_readonly(form):
    form.readonly = True
    for field in form.fields.values():
        if isinstance(field.widget, (forms.TextInput, forms.Textarea)):
            field.widget.attrs['readonly'] = 'readonly'
            field.widget.attrs['placeholder'] = \
                '-- {0} --'.format(_('No information given'))
        else:
            field.widget.attrs['readonly'] = 'readonly'
            field.widget.attrs['disabled'] = 'disabled'

class ReadonlyFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        super().__init__(*args, **kwargs)
        if self.readonly:
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
