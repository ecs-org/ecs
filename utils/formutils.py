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
        new_class = super(TranslatedModelFormMetaclass, cls).__new__(cls, name, bases, attrs)

        try:
            parents = [b for b in bases if issubclass(b, TranslatedModelForm)]
        except NameError:
            parents = None
        if not parents:
            return new_class

        opts = new_class._meta = TranslatedModelFormOptions(getattr(new_class, 'Meta', None))

        if opts.labels:
            for name, label in opts.labels.iteritems():
                new_class.base_fields[name].label = label

        return new_class

class TranslatedModelForm(ModelForm):
    __metaclass__ = TranslatedModelFormMetaclass
