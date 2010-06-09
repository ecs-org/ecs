from django import forms
from django.contrib.auth.models import User

class UserSwitcherForm(forms.Form):
    user = forms.ModelChoiceField(User.objects.filter(username__contains="Testuser").order_by('username'), required=False, label=u'Benutzer')