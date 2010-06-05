from django import forms

from ecs.core.models import Vote

class VoteForm(forms.ModelForm):
    result = Vote._meta.get_field('result').formfield(widget=forms.RadioSelect(), required=True)

    class Meta:
        model = Vote
        exclude = ('top',)