from django import forms
from django.contrib.auth.models import Group

class GroupChooserForm(forms.Form):
    group = forms.ModelChoiceField(Group.objects.order_by('name'), required=False, label=u'Gruppe')