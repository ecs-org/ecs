from django import forms
from django.utils.translation import ugettext_lazy as _
from ecs.notifications.models import NotificationAnswer


class NotificationAnswerForm(forms.ModelForm):
    class Meta:
        model = NotificationAnswer
        fields = ('text',)


class RejectableNotificationAnswerForm(NotificationAnswerForm):
    rejected = forms.BooleanField(required=False)

    class Meta:
        model = NotificationAnswer
        fields = ('rejected', 'text',)

