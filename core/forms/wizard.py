# -*- coding: utf-8 -*-

import new

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse

from ecs.core.models.submissions import SubmissionForm


def _create_wizard_form(name, definition):
    _fields = {
        'name': forms.CharField(widget=forms.HiddenInput(attrs={'value': name})),
        'next': forms.CharField(widget=forms.HiddenInput(attrs={'value': 'submission'})),
    }
    _fields.update(definition['fields'])

    

    class _WizardForm(forms.ModelForm):
        def is_terminal(self):
            return self.cleaned_data['next'] == 'end'

        def get_next(self):
            definition = wizard_forms[self.cleaned_data['next']]
            obj = None
            if definition['type'] == 'wizard':
                obj = _create_wizard_form(self.cleaned_data['next'], definition)
            elif definition['type'] == 'redirect':
                obj = definition['redirect_url']

            return (definition['type'], obj)

        class Meta:
            model = SubmissionForm
            fields = tuple(_fields.keys())

    for fieldname in _fields.iterkeys():
        setattr(_WizardForm, fieldname, _fields[fieldname])

    return type('WizardForm', (forms.ModelForm,), dict(_WizardForm.__dict__))


wizard_forms = {
    'start': {
        'type': 'wizard',
        'fields': {
            'next': forms.ChoiceField(choices=(
                ('end',    _('Empty Study')),
                ('thesis', _('Thesis')),
                ('amg',    _('AMG-Study')),
                ('mpg',    _('MPG-Study')),
                ('import', _('Import Submission')),
            )),
        },
    },
    'thesis': {
        'type': 'wizard',
        'fields': {
            'next': forms.ChoiceField(choices=(
                ('thesis_meduni_vienna',    _('at Medical University Vienna')),
                ('thesis_other_university', _('other University')),
            )),
        },
    },
    'thesis_meduni_vienna': {
        'type': 'wizard',
        'fields': {},
    },
    'thesis_other_university': {
        'type': 'wizard',
        'fields': {},
    },
    'amg': {
        'type': 'wizard',
        'fields': {},
    },
    'mpg': {
        'type': 'wizard',
        'fields': {},
    },
    'import': {
        'type': 'redirect',
        'redirect_url': reverse('ecs.core.views.import_submission_form'),
    },
}


def get_wizard_form(name):
    definition = wizard_forms[name]
    if not definition['type'] == 'wizard':
        raise KeyError()

    return _create_wizard_form(name, definition)


