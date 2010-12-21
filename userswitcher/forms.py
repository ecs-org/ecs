# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ecs.users.forms import UserChoiceField


class UserSwitcherForm(forms.Form):
    user = UserChoiceField(
        User.objects.filter(groups__name='userswitcher_target').order_by('email'), 
        required=False, 
        label=_(u'user'), 
        widget=forms.Select(attrs={'id': 'userswitcher_input'})
    )


