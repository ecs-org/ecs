from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from ecs.communication.models import Message, Thread

class SendMessageForm(forms.ModelForm):
    subject = Thread._meta.get_field('subject').formfield()
    
    class Meta:
        model = Message
        fields = ( 'text','receiver')
        
class ReplyToMessageForm(forms.ModelForm):
    subject = Thread._meta.get_field('subject').formfield()
    
    class Meta:
        model = Message
        fields = ('text',)
        
class ThreadDelegationForm(forms.Form):
    to = forms.ModelChoiceField(User.objects.all())
    text = Message._meta.get_field('text').formfield()
