from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db.models import Q

from ecs.core.forms.fields import AutocompleteModelChoiceField
from ecs.pki.models import Certificate


class CertForm(forms.Form):
    user = AutocompleteModelChoiceField(
        'pki-users',
        User.objects.filter(
            Q(profile__is_internal=True) | Q(profile__is_omniscient_member=True),
            is_active=True
        )
    )
    cn = forms.CharField()
    
    def clean(self):
        cd = super().clean()
        
        user = cd.get('user')
        if user:
            cn = cd.get('cn')
            if Certificate.objects.filter(cn=cn).exists():
                self.add_error('cn', _('A certificate with this CN already exists.'))

        return cd
        
