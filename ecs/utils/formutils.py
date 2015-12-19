# -*- coding: utf-8 -*-

from django.forms.models import ModelForm, ModelFormMetaclass, ModelFormOptions
from django.core.validators import EMPTY_VALUES
from django.utils.importlib import import_module

def require_fields(form, fields):
    for f in fields:
        if f not in form.cleaned_data or form.cleaned_data[f] in EMPTY_VALUES:
            form.add_error(f, form.fields[f].error_messages['required'])

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


def _unpickle(module, cls_name, args, kwargs):
    form_cls = getattr(import_module(module), cls_name)
    instance_id = kwargs.pop('instance_id', None)
    if not instance_id is None:
        kwargs['instance'] = form_cls._meta.model.objects.get(id=instance_id)
    return form_cls(*args, **kwargs)

class ModelFormPickleMixin(object):
    def __reduce__(self):
        kwargs = {'data': self.data or None, 'prefix': self.prefix, 'initial': self.initial}
        if not self.instance.id is None:
            kwargs['instance_id'] = self.instance.id
        return (_unpickle, (self.__class__.__module__, self.__class__.__name__, (), kwargs))
