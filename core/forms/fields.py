from django import forms

from ecs.core.models import Investigator

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

class InvestigatorChoiceMixin(object):
    def __init__(self, **kwargs):
        kwargs.setdefault('queryset', Investigator.objects.order_by('name'))
        super(InvestigatorChoiceMixin, self).__init__(**kwargs)

    def label_from_instance(self, obj):
        return u"%s (%s)" % (obj.name, obj.ethics_commission.name)

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