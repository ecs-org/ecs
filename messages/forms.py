from django import forms

from ecs.messages.models import Message

class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('subject', 'receiver', 'text')
        
class ReplyToMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('subject', 'text')