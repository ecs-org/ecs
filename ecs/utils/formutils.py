from importlib import import_module

from django.forms.models import ModelForm, ModelFormMetaclass, ModelFormOptions
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet


def require_fields(form, fields):
    for f in fields:
        val = form.cleaned_data.get(f, None)
        if val in EMPTY_VALUES or \
            (isinstance(val, QuerySet) and not val.exists()):
            form.add_error(f, form.fields[f].error_messages['required'])


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
