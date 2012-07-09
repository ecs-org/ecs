# -*- coding: utf-8 -*-
from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.utils.formutils import TranslatedModelForm
from ecs.votes.models import Vote
from ecs.tasks.models import Task
from ecs.votes.constants import PERMANENT_VOTE_RESULTS, VOTE_PREPARATION_CHOICES, B2_VOTE_PREPARATION_CHOICES
from ecs.users.utils import sudo, get_current_user
from ecs.core.forms.utils import mark_readonly

def ResultField(**kwargs):
    return Vote._meta.get_field('result').formfield(widget=forms.RadioSelect(), **kwargs)

class SaveVoteForm(forms.ModelForm):
    result = ResultField(required=False)
    close_top = forms.BooleanField(required=False)
    executive_review_required = forms.NullBooleanField(widget=forms.HiddenInput())

    class Meta:
        model = Vote
        exclude = ('top', 'submission_form', 'submission', 'published_at', 'is_final_version', 'signed_at', 'valid_until', 
            'upgrade_for', 'insurance_review_required')

    def save(self, top, *args, **kwargs):
        kwargs['commit'] = False
        instance = super(SaveVoteForm, self).save(*args, **kwargs)
        instance.top = top
        instance.save()
        return instance

class VoteForm(SaveVoteForm):
    result = ResultField(required=True)

    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        super(VoteForm, self).__init__(*args, **kwargs)
        if self.readonly:
            mark_readonly(self)

class VoteReviewForm(ReadonlyFormMixin, TranslatedModelForm):
    class Meta:
        model = Vote
        fields = ('text', 'is_final_version')
        labels = {
            'is_final_version': _('Proofread and valid'),
        }

    def __init__(self, *args, **kwargs):
        super(VoteReviewForm, self).__init__(*args, **kwargs)
        user = get_current_user()
        if not self.readonly and user.get_profile().is_executive_board_member:
            self.fields['result'] = ResultField(required=True, initial=self.instance.result)

    def clean(self):
        cleaned_data = super(VoteReviewForm, self).clean()
        if 'result' in self.fields:
            original_result = self.instance.result
            result = cleaned_data['result']
            print original_result
            print result
            if not result == original_result and 'is_final_version' in cleaned_data:
                del cleaned_data['is_final_version']
        return cleaned_data

    def save(self, commit=True):
        instance = super(VoteReviewForm, self).save(commit=False)
        if 'result' in self.fields:
            original_result = instance.result
            instance.result = self.cleaned_data['result']
            if not instance.result == original_result:
                instance.is_final_version = False
                instance.changed_after_voting = True
        if commit:
            instance.save()


class VotePreparationForm(forms.ModelForm):
    result = ResultField(choices=VOTE_PREPARATION_CHOICES, required=True)

    class Meta:
        model = Vote
        fields = ('result', 'text')

    def save(self, commit=True):
        vote = super(VotePreparationForm, self).save(commit=False)
        vote.is_draft = True
        if commit:
            vote.save()
        return vote


class B2VotePreparationForm(forms.ModelForm):
    result = ResultField(choices=B2_VOTE_PREPARATION_CHOICES, required=True)
    
    class Meta:
        model = Vote
        fields = ('result', 'text')
