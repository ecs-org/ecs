from django import forms
from django.utils.translation import ugettext_lazy as _

class MedicalCategoryCreationForm(forms.Form):
    name = forms.CharField(label=_('name'), max_length=60)
    abbrev = forms.CharField(label=_('Shorthand Symbol'), max_length=12)

    def __init__(self, data):
        super().__init__(data=data)