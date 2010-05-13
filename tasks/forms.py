from django import forms
from django.contrib.auth.models import User

class DelegateTaskForm(forms.Form):
    user = forms.ModelChoiceField(User.objects.all())
    message = forms.CharField(required=False)
    
class DeclineTaskForm(forms.Form):
    message = forms.CharField(required=False)