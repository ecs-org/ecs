from django import forms
from ecs.notifications.models import NotificationAnswer


class NotificationAnswerForm(forms.ModelForm):
    class Meta:
        model = NotificationAnswer
        fields = ('valid', 'text',)