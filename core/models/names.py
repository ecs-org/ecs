from django.db import models
from django.utils.translation import ugettext_lazy as _

class Name(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def salutation(self):
        if not self.gender:
            return ''
        return self.gender == 'f' and 'Frau' or 'Herr'

    @property
    def full_name(self):
        return " ".join(bit for bit in [self.salutation, self.first_name, self.last_name] if bit).strip()
        
    def __unicode__(self):
        return self.full_name


class NameField(object):
    def __init__(self, required=None):
        self.required = required or []
        return super(NameField, self).__init__()

    def __get__(self, obj, obj_type=None):
        if not obj:
            return self
        return Name(**dict((field, getattr(obj, '%s_%s' % (self.name, field))) for field in ('gender', 'title', 'first_name', 'last_name')))
        
    def contribute_to_class(self, cls, name):
        self.name = name

        flist = (
            ('gender', models.CharField, {'max_length': 1, 'choices': (('f', _('Ms')), ('m', _('Mr'))), 'null': True}),
            ('title', models.CharField, {'max_length': 30}),
            ('first_name', models.CharField, {'max_length': 50}),
            ('last_name', models.CharField, {'max_length': 50}),
        )

        for fname, fcls, fkwargs in flist:
            fkwargs['blank'] = not fname in self.required
            fcls(**fkwargs).contribute_to_class(cls, '{0}_{1}'.format(name, fname))
        
        setattr(cls, name, self)
        
