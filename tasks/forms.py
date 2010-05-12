from django import forms
from django.contrib.auth.models import User

class DelegateTaskForm(forms.Form):
    user = forms.ModelChoiceField(User)
    message = forms.TextField(required=False)
    
class DeclineTaskForm(forms.Form):
    message = forms.TextField(required=False)