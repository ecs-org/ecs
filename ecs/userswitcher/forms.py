from django import forms
from django.contrib.auth.models import User

class _UserSwitcherChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        queryset = User.objects.filter(groups__name='userswitcher_target', is_active=True).select_related('profile').order_by('last_name', 'first_name', 'email')
        defaults = {
            'required': False,
            'widget': forms.Select(attrs={'id': 'userswitcher_input'}),
        }
        for k, v in defaults.items():
            kwargs.setdefault(k, v)
        super(_UserSwitcherChoiceField, self).__init__(queryset, *args, **kwargs)

    def label_from_instance(self, user):
        label = str(user.email)
        if user.first_name and user.last_name:
            label = '{0}, {1}'.format(user.last_name, user.first_name)
        return label

class UserSwitcherForm(forms.Form):
    user = _UserSwitcherChoiceField()
