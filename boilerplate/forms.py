from django import forms
from ecs.boilerplate.models import Text

class TextForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ('slug', 'text')