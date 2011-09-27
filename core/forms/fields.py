# -*- coding: utf-8 -*
import datetime

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ecs.utils.timedelta import parse_timedelta
from ecs.users.utils import get_user

DATE_INPUT_FORMATS = ("%d.%m.%Y", "%Y-%m-%d")
TIME_INPUT_FORMATS = ("%H:%M", "%H:%M:%S")
DATE_TIME_INPUT_FORMATS = tuple("%s %s" % (date_format, time_format) for time_format in TIME_INPUT_FORMATS for date_format in DATE_INPUT_FORMATS)


class LooseTimeWidget(forms.TextInput):
    def _format_value(self, value):
        if isinstance(value, datetime.time):
            return value.strftime('%H:%M')
        return value

class DateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', DATE_INPUT_FORMATS)
        kwargs.setdefault('error_messages', {'invalid': _(u'Please enter a date in the format dd.mm.yyyy.')})
        super(DateField, self).__init__(*args, **kwargs)

class DateTimeField(forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', DATE_TIME_INPUT_FORMATS)
        kwargs.setdefault('widget', forms.SplitDateTimeWidget(date_format=DATE_INPUT_FORMATS[0]))
        kwargs.setdefault('error_messages', {'invalid': _(u'Please enter a date in dd.mm.yyyy format and time in format HH:MM.')})
        super(DateTimeField, self).__init__(*args, **kwargs)

class TimeField(forms.TimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('error_messages', {'invalid': _(u'Please enter a time in the format HH: MM.')})
        kwargs.setdefault('widget', LooseTimeWidget())
        super(TimeField, self).__init__(*args, **kwargs)
        
class TimedeltaField(forms.CharField):
    default_error_messages = {
        'invalid': _(u'Please enter a valid time period. E.g. "10min" or "1h 30min"'),
    }
    def to_python(self, value):
        try:
            return parse_timedelta(super(TimedeltaField, self).to_python(value))
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])


class NullBooleanWidget(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', u'-'), (u'2', _(u'Yes')), (u'3', _(u'No')))
        forms.widgets.Select.__init__(self, attrs, choices)

class NullBooleanField(forms.NullBooleanField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', NullBooleanWidget)
        super(NullBooleanField, self).__init__(*args, **kwargs)
        
class MultiselectWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        return super(MultiselectWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        value_list = ",".join(map(str, value or ()))
        attrs['class'] = 'autocomplete'
        url = self.url
        if callable(url):
            url = url()
        attrs['x-autocomplete-url'] = url
        attrs['x-autocomplete-type'] = 'multi'
        return super(MultiselectWidget, self).render(name, value_list, attrs=attrs)
        
    def value_from_datadict(self, data, files, name):
        val = data.get(name, '')
        if not val:
            return []
        return val.split(',')

class SingleselectWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        return super(SingleselectWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        value_list = str(value) if value else ''
        attrs['class'] = 'autocomplete'
        url = self.url
        if callable(url):
            url = url()
        attrs['x-autocomplete-url'] = url
        attrs['x-autocomplete-type'] = 'single'
        return super(SingleselectWidget, self).render(name, value_list, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        val = data.get(name, '')
        vals = val.split(',')
        if not val:
            return None
        return val.split(',')[0]

from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode

class ReadonlyTextMixin(object):
    def __init__(self, *args, **kwargs):
        super(ReadonlyTextMixin, self).__init__(*args, **kwargs)
        self.readonly = False

    def mark_readonly(self):
        self.readonly = True

    def render(self, name, value, attrs=None):
        if not self.readonly:
            return super(ReadonlyTextMixin, self).render(name, value, attrs=attrs)
        else:
            if value is None: value = ''
            if attrs is None: attrs = {}
            if not value:
                attrs['class'] += ' empty'
            final_attrs = self.build_attrs(attrs, name=name)
            empty_str = u'<em>-- {0} --</em>'.format(_(u'No information given'))
            return mark_safe(u'<pre{0}>{1}</pre>'.format(flatatt(final_attrs), conditional_escape(force_unicode(value)) or empty_str))

class ReadonlyTextInput(ReadonlyTextMixin, forms.TextInput):
    def render(self, name, value, attrs=None):
        if attrs is None: attrs = {}
        if self.readonly:
            attrs['class'] = 'oneline'
        return super(ReadonlyTextInput, self).render(name, value, attrs=attrs)

class ReadonlyTextarea(ReadonlyTextMixin, forms.Textarea):
    def render(self, name, value, attrs=None):
        if attrs is None: attrs = {}
        if self.readonly:
            attrs['class'] = 'multiline'
            if not 'cols' in attrs and not 'cols' in self.attrs:
                attrs['cols'] = 100
        return super(ReadonlyTextarea, self).render(name, value, attrs=attrs)

class StrippedTextInput(ReadonlyTextInput):
    def value_from_datadict(self, *args, **kwargs):
        v = super(StrippedTextInput, self).value_from_datadict(*args, **kwargs)
        if v is not None:
            v = v.strip()
        return v

class EmailUserSelectWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        else:
            value = User.objects.get(pk=value).email
        return super(EmailUserSelectWidget, self).render(name, value, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        val = data.get(name, '')
        if not val:
            return None
        try:
            return get_user(val.strip()).pk
        except User.DoesNotExist:
            return None
