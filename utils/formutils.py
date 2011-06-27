# -*- coding: utf-8 -*-

from django.forms.models import ModelForm, ModelFormMetaclass, ModelFormOptions
from django.core.validators import EMPTY_VALUES

def require_fields(form, fields):
    for f in fields:
        if f not in form.cleaned_data or form.cleaned_data[f] in EMPTY_VALUES:
            form._errors[f] = form.error_class([form.fields[f].error_messages['required']])

class TranslatedModelFormOptions(ModelFormOptions):
    def __init__(self, options=None):
        super(TranslatedModelFormOptions, self).__init__(options=options)
        self.labels = getattr(options, 'labels', None)

class TranslatedModelFormMetaclass(ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        newcls = super(TranslatedModelFormMetaclass, cls).__new__(cls, name, bases, attrs)

        try:
            parents = [b for b in bases if issubclass(b, TranslatedModelForm)]
        except NameError:
            parents = None
        if not parents:
            return newcls

        opts = newcls._meta = TranslatedModelFormOptions(getattr(newcls, 'Meta', None))

        if opts.labels:
            for name, label in opts.labels.iteritems():
                newcls.base_fields[name].label = label

        return newcls

class TranslatedModelForm(ModelForm):
    __metaclass__ = TranslatedModelFormMetaclass
