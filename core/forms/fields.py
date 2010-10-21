# -*- coding: utf-8 -*
from django import forms
from django.utils.safestring import mark_safe

from ecs.core.models import Investigator
from ecs.utils.timedelta import parse_timedelta

DATE_INPUT_FORMATS = ("%d.%m.%Y", "%Y-%m-%d")
TIME_INPUT_FORMATS = ("%H:%M", "%H:%M:%S")
DATE_TIME_INPUT_FORMATS = tuple("%s %s" % (date_format, time_format) for time_format in TIME_INPUT_FORMATS for date_format in DATE_INPUT_FORMATS)

class DateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', DATE_INPUT_FORMATS)
        kwargs.setdefault('error_messages', {'invalid': u'Bitte geben Sie ein Datum im Format TT.MM.JJJJ ein.'})
        super(DateField, self).__init__(*args, **kwargs)

class DateTimeField(forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', DATE_TIME_INPUT_FORMATS)
        kwargs.setdefault('widget', forms.SplitDateTimeWidget(date_format=DATE_INPUT_FORMATS[0]))
        kwargs.setdefault('error_messages', {'invalid': u'Bitte geben Sie ein Datum im Format TT.MM.JJJJ und eine Uhrzeit im Format HH:MM ein.'})
        super(DateTimeField, self).__init__(*args, **kwargs)

class TimeField(forms.TimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('error_messages', {'invalid': u'Bitte geben Sie eine Uhrzeit im Format HH:MM ein.'})
        super(TimeField, self).__init__(*args, **kwargs)
        
class TimedeltaField(forms.CharField):
    default_error_messages = {
        'invalid': u'Bitte geben Sie eine gültige Zeitspanne an. Z.b. "10min" oder "1h 30min"',
    }
    def to_python(self, value):
        try:
            return parse_timedelta(super(TimedeltaField, self).to_python(value))
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])

class InvestigatorChoiceMixin(object):
    def __init__(self, **kwargs):
        kwargs.setdefault('queryset', Investigator.objects.order_by('contact_last_name', 'contact_first_name'))
        super(InvestigatorChoiceMixin, self).__init__(**kwargs)

    def label_from_instance(self, obj):
        return u"%s (%s)" % (obj.contact_last_name, obj.ethics_commission.name) # FIXME: use the full contact name

class InvestigatorChoiceField(InvestigatorChoiceMixin, forms.ModelChoiceField): pass
class InvestigatorMultipleChoiceField(InvestigatorChoiceMixin, forms.ModelMultipleChoiceField): pass

class NullBooleanWidget(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', u'-'), (u'2', u'Ja'), (u'3', u'Nein'))
        forms.widgets.Select.__init__(self, attrs, choices)

class NullBooleanField(forms.NullBooleanField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', NullBooleanWidget)
        super(NullBooleanField, self).__init__(*args, **kwargs)
        
class MultiselectWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        super(MultiselectWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        value_list = ",".join(map(str, value))
        attrs['class'] = 'autocomplete'
        url = self.url
        if callable(url):
            url = url()
        attrs['x-autocomplete-url'] = url
        return super(MultiselectWidget, self).render(name, value_list, attrs=attrs)
        
    def value_from_datadict(self, data, files, name):
        val = data.get(name, '')
        if not val:
            return []
        return val.split(',')
        
