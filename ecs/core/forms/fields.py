import datetime

from django import forms
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.contrib.auth.models import User
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
        super().__init__(*args, **kwargs)

class DateTimeField(forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', DATE_TIME_INPUT_FORMATS)
        kwargs.setdefault('widget', forms.SplitDateTimeWidget(date_format=DATE_INPUT_FORMATS[0]))
        kwargs.setdefault('error_messages', {'invalid': _('Please enter a date in dd.mm.yyyy format and time in format HH:MM.')})
        super().__init__(*args, **kwargs)

class TimeField(forms.TimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('error_messages', {'invalid': _('Please enter a time in the format HH: MM.')})
        kwargs.setdefault('widget', LooseTimeWidget())
        super().__init__(*args, **kwargs)
        
class NullBooleanWidget(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = (('1', '-'), ('2', _('Yes')), ('3', _('No')))
        forms.widgets.Select.__init__(self, attrs, choices)

class NullBooleanField(forms.NullBooleanField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', NullBooleanWidget)
        super().__init__(*args, **kwargs)


class AutocompleteWidgetMixin(object):
    def __init__(self, field):
        self.field = field
        return super().__init__()

    def render(self, name, value, attrs=None, choices=()):
        attrs['data-ajax--url'] = reverse(
            'ecs.core.views.autocomplete.autocomplete',
            kwargs={'queryset_name': self.field.queryset_name}
        )
        return super().render(name, value, attrs=attrs)

    def render_options(self, choices, selected_choices):
        selected_choices = set(force_text(v) for v in selected_choices if v != '')
        output = []
        objs = self.field.queryset.filter(pk__in=selected_choices)
        for obj in objs:
            option_value = self.field.prepare_value(obj)
            option_label = self.field.label_from_instance(obj)
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)


class AutocompleteFieldMixin:
    def __init__(self, queryset_name, queryset, **kwargs):
        self.queryset_name = queryset_name
        kwargs['widget'] = self.widget(self)
        super().__init__(queryset, **kwargs)

class AutocompleteModelChoiceField(AutocompleteFieldMixin, forms.ModelChoiceField):
    class widget(AutocompleteWidgetMixin, forms.Select):
        pass


class AutocompleteModelMultipleChoiceField(AutocompleteFieldMixin, forms.ModelMultipleChoiceField):
    class widget(AutocompleteWidgetMixin, forms.SelectMultiple):
        pass


class StrippedTextInput(forms.TextInput):
    def value_from_datadict(self, *args, **kwargs):
        v = super().value_from_datadict(*args, **kwargs)
        if v is not None:
            v = v.strip()
        return v


class EmailUserSelectWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        else:
            value = User.objects.get(pk=value).email
        return super().render(name, value, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        val = data.get(name, '')
        if not val:
            return None
        try:
            return get_user(val.strip()).pk
        except User.DoesNotExist:
            return None
