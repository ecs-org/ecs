from django import forms
from django.utils.translation import ugettext_lazy as _

from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.votes.models import Vote
from ecs.votes.constants import VOTE_PREPARATION_CHOICES, B2_VOTE_PREPARATION_CHOICES
from ecs.users.utils import get_current_user
from ecs.core.forms.utils import mark_readonly

def ResultField(**kwargs):
    return Vote._meta.get_field('result').formfield(widget=forms.RadioSelect(), **kwargs)

class SaveVoteForm(forms.ModelForm):
    result = ResultField(required=False)
    close_top = forms.BooleanField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Vote
        fields = ('result', 'text')

    def save(self, top, *args, **kwargs):
        kwargs['commit'] = False
        instance = super().save(*args, **kwargs)
        instance.submission_form = top.submission.current_submission_form
        instance.top = top
        instance.save()
        return instance

class VoteForm(SaveVoteForm):
    result = ResultField(required=True)

    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        super().__init__(*args, **kwargs)
        if self.readonly:
            mark_readonly(self)

class VoteReviewForm(ReadonlyFormMixin, forms.ModelForm):
    class Meta:
        model = Vote
        fields = ('text', 'is_final_version')
        labels = {
            'is_final_version': _('Proofread and valid'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = get_current_user()
        if not self.readonly and user.profile.is_executive:
            self.fields['result'] = Vote._meta.get_field('result').formfield(
                initial=self.instance.result)

            # reorder fields
            self.fields['text'] = self.fields.pop('text')
            self.fields['is_final_version'] = self.fields.pop('is_final_version')

    def clean(self):
        cleaned_data = super().clean()
        if 'result' in self.fields:
            original_result = self.instance.result
            result = cleaned_data['result']
            if not result == original_result and 'is_final_version' in cleaned_data:
                del cleaned_data['is_final_version']
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if 'result' in self.fields:
            original_result = instance.result
            instance.result = self.cleaned_data['result']
            if not instance.result == original_result:
                instance.is_final_version = False
                instance.changed_after_voting = True
        if commit:
            instance.save()


class VotePreparationForm(forms.ModelForm):
    result = Vote._meta.get_field('result').formfield(
        choices=VOTE_PREPARATION_CHOICES)

    class Meta:
        model = Vote
        fields = ('result', 'text')

    def save(self, commit=True):
        vote = super().save(commit=False)
        vote.is_draft = True
        if commit:
            vote.save()
        return vote


class B2VotePreparationForm(forms.ModelForm):
    result = Vote._meta.get_field('result').formfield(
        choices=B2_VOTE_PREPARATION_CHOICES)
    
    class Meta:
        model = Vote
        fields = ('result', 'text')
