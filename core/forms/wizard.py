# -*- coding: utf-8 -*-

import new

from django.utils.translation import ugettext as _
from django import forms

from ecs.core.models.submissions import SubmissionForm


def _create_wizard_form(name, definition):
    _fields = {
        'name': forms.CharField(widget=forms.HiddenInput(attrs={'value': name})),
        'next': forms.CharField(widget=forms.HiddenInput(attrs={'value': 'submission'})),
    }
    _fields.update(definition)

    class _WizardForm(forms.ModelForm):
        def is_terminal(self):
            return self.cleaned_data['next'] == 'end'

        def get_next(self):
            return get_wizard_form(self.cleaned_data['next'])

        class Meta:
            model = SubmissionForm
            fields = tuple(_fields.keys())

    for fieldname in _fields.iterkeys():
        setattr(_WizardForm, fieldname, _fields[fieldname])


    print _WizardForm.Meta.fields
    return type('WizardForm', (forms.ModelForm,), dict(_WizardForm.__dict__))


wizard_forms = {
    'start': {
        #'next': forms.ChoiceField(choices=(('end', _('Leere Studie anlegen')), ('thesis', _('thesis')), ('import', _('Import Submission')))),
        'next': forms.ChoiceField(choices=(('end', _('Leere Studie anlegen')),)),
    },

}

def get_wizard_form(name):
    return _create_wizard_form(name, wizard_forms[name])


