from django import forms
from django.contrib.auth.models import User

class UserSwitcherForm(forms.Form):
    #user = forms.ModelChoiceField(User.objects.filter(username__contains="Testuser").order_by('username'), required=False, label=u'Benutzer')
    user = forms.ModelChoiceField(
        User.objects.filter(groups__name='userswitcher_target').order_by('username'), 
        required=False, 
        label=u'Benutzer', 
        widget=forms.Select(attrs={'id': 'userswitcher_input'})
    )
