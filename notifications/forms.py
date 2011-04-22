from django import forms
from django.utils.translation import ugettext_lazy as _
from ecs.notifications.models import NotificationAnswer


class NotificationAnswerForm(forms.ModelForm):
    valid = forms.BooleanField(label=_('valid'))
    class Meta:
        model = NotificationAnswer
        fields = ('valid', 'text',)