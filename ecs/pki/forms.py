from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.core.forms.fields import SingleselectWidget
from ecs.pki.models import Certificate

mandatory = getattr(settings, 'ECS_MANDATORY_CLIENT_CERTS', False)
user_queryset_name = 'users' if mandatory else 'internal-users'

class CertForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True) if mandatory else User.objects.filter(is_active=True, profile__is_internal=True),
        widget=SingleselectWidget(url=lambda: reverse('ecs.core.views.autocomplete.internal_autocomplete', kwargs={'queryset_name': user_queryset_name}))
    )
    cn = forms.CharField()
    passphrase = forms.CharField(widget=forms.PasswordInput(), min_length=12)
    passphrase2 = forms.CharField(widget=forms.PasswordInput())
    
    def clean(self):
        cd = super(CertForm, self).clean()
        
        user = cd.get('user')
        if user:
            cn = cd.get('cn')
            if Certificate.objects.filter(cn=cn).exists():
                self.add_error('cn', _('A certificate with this CN already exists.'))

        if cd.get('passphrase') != cd.get('passphrase2'):
            self.add_error('passphrase2', _('The passphrases do not match.'))
        return cd
        
