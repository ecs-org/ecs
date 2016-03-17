import random
import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from ecs.tags.models import Tag


class ColorInput(forms.TextInput):
    input_type = 'color'


class ColorField(forms.Field):
    widget = ColorInput

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = lambda: random.randint(0, 0xffffff)
        super(ColorField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        try:
            m = re.match(r'#[0-9A-Fa-f]{6}$', value)
        except TypeError:
            m = None
        if not m:
            raise forms.ValidationError(self.error_message['invalid'], code='invalid')
        return int(value[1:], 16)

    def prepare_value(self, value):
        if isinstance(value, int):
            return '#{:06x}'.format(value)
        return value


class TagForm(forms.ModelForm):
    color = ColorField(label=_('Color'))

    class Meta:
        model = Tag
        fields = ('name', 'color')
        labels = {
            'name': _('Name'),
        }


class TagMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, **kwargs):
        super(TagMultipleChoiceField, self).__init__(Tag.objects, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class TagAssignForm(forms.Form):
    tags = TagMultipleChoiceField(required=False)
