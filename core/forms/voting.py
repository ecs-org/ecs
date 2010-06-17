from django import forms

from ecs.core.models import Vote

def ResultField(**kwargs):
    return Vote._meta.get_field('result').formfield(widget=forms.RadioSelect(), **kwargs)

class VoteForm(forms.ModelForm):
    result = ResultField(required=True)
    close_top = forms.BooleanField(required=False)
    executive_review_required = forms.NullBooleanField(widget=forms.HiddenInput())

    class Meta:
        model = Vote
        exclude = ('top',)
        
class SaveVoteForm(VoteForm):
    result = ResultField(required=False)
    

class VoteReviewForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ('result', 'text')
    