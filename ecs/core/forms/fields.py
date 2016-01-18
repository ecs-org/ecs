import datetime

from django import forms
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

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
        kwargs.setdefault('error_messages', {'invalid': _('Please enter a date in the format dd.mm.yyyy.')})
        super(DateField, self).__init__(*args, **kwargs)

class DateTimeField(forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', DATE_TIME_INPUT_FORMATS)
        kwargs.setdefault('widget', forms.SplitDateTimeWidget(date_format=DATE_INPUT_FORMATS[0]))
        kwargs.setdefault('error_messages', {'invalid': _('Please enter a date in dd.mm.yyyy format and time in format HH:MM.')})
        super(DateTimeField, self).__init__(*args, **kwargs)

class TimeField(forms.TimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('error_messages', {'invalid': _('Please enter a time in the format HH: MM.')})
        kwargs.setdefault('widget', LooseTimeWidget())
        super(TimeField, self).__init__(*args, **kwargs)
        
class BooleanWidget(forms.widgets.Select):
    def __init__(self, attrs=None):
        choices = ((True, _('Yes')), (False, _('No')))
        super(BooleanWidget, self).__init__(attrs, choices)

class NullBooleanWidget(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = (('1', '-'), ('2', _('Yes')), ('3', _('No')))
        forms.widgets.Select.__init__(self, attrs, choices)

class NullBooleanField(forms.NullBooleanField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', NullBooleanWidget)
        super(NullBooleanField, self).__init__(*args, **kwargs)


class AutocompleteMixin(object):
    def __init__(self, queryset_name, *args, **kwargs):
        self.queryset_name = queryset_name
        return super(AutocompleteMixin, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        attrs['data-ajax--url'] = reverse(
            'ecs.core.views.autocomplete.autocomplete',
            kwargs={'queryset_name': self.queryset_name}
        )
        attrs['data-placeholder'] = _('Start typing to receive suggestions.')
        return super(AutocompleteMixin, self).render(name, value, attrs=attrs)

    def render_option(self, selected_choices, option_value, option_label):
        if force_text(option_value or '') not in selected_choices:
            return ''
        return super(AutocompleteMixin, self).render_option(selected_choices, option_value, option_label)

class MultiAutocompleteWidget(AutocompleteMixin, forms.SelectMultiple):
    pass

class AutocompleteWidget(AutocompleteMixin, forms.Select):
    pass


from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from django.utils.html import conditional_escape

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
            empty_str = '<em>-- {0} --</em>'.format(_('No information given'))
            return mark_safe('<pre{0}>{1}</pre>'.format(flatatt(final_attrs), conditional_escape(force_text(value)) or empty_str))

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
