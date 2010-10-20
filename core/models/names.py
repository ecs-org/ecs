from django.db import models


class Name(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def salutation(self):
        return self.gender == 'f' and 'Frau' or 'Herr'

    @property
    def full_name(self):
        return " ".join(bit for bit in [self.salutation, self.first_name, self.last_name] if bit).strip()


class NameField(object):
    def __get__(self, obj, obj_type=None):
        if not obj:
            return self
        return Name(**dict((field, getattr(obj, '%s_%s' % (self.name, field))) for field in ('gender', 'title', 'first_name', 'last_name')))
        
    def contribute_to_class(self, cls, name):
        self.name = name
        fields = {
            'gender': models.CharField(max_length=1, choices=(('f', 'Frau'), ('m', 'Herr')), blank=True, null=True),
            'title': models.CharField(max_length=30, blank=True),
            'first_name': models.CharField(max_length=50, blank=True),
            'last_name': models.CharField(max_length=50, blank=True),
        }
        for fieldname, field in fields.items():
            field.contribute_to_class(cls, "%s_%s" % (name, fieldname))
        
        setattr(cls, name, self)
        
