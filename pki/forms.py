from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from ecs.core.forms.fields import SingleselectWidget
from ecs.pki.models import Certificate

class CertForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(ecs_profile__is_internal=True), 
        widget=SingleselectWidget(url=lambda: reverse('ecs.core.views.internal_autocomplete', kwargs={'queryset_name': 'internal-users'}))
    )
    cn = forms.CharField(required=False)
    passphrase = forms.CharField(required=True, min_length=8)
    passphrase2 = forms.CharField(required=True)
    
    def clean(self):
        cd = super(CertForm, self).clean()
        
        user = cd.get('user')
        if user:
            cn = cd.get('cn')
            if Certificate.objects.filter(cn=cn, is_revoked=False).exists():
                self._errors['cn'] = self.error_class([_('A certificate with this CN already exists.')])

        if cd.get('passphrase') != cd.get('passphrase2'):
            self._errors['passphrase2'] = self.error_class([_('The passphrases do not match.')])
        return cd
        
