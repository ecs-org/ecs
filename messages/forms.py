from django import forms

from ecs.messages.models import Message, Thread

class SendMessageForm(forms.ModelForm):
    subject = Thread._meta.get_field('subject').formfield()

    class Meta:
        model = Message
        fields = ('receiver', 'text',)
        
class ReplyToMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text',)