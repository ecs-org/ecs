# -*- coding: utf-8 -*-
from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.utils.formutils import TranslatedModelForm
from ecs.votes.models import Vote
from ecs.tasks.models import Task
from ecs.votes.constants import PERMANENT_VOTE_RESULTS, VOTE_PREPARATION_CHOICES
from ecs.users.utils import sudo

def ResultField(**kwargs):
    return Vote._meta.get_field('result').formfield(widget=forms.RadioSelect(), **kwargs)

class SaveVoteForm(forms.ModelForm):
    result = ResultField(required=False)
    close_top = forms.BooleanField(required=False)
    executive_review_required = forms.NullBooleanField(widget=forms.HiddenInput())

    class Meta:
        model = Vote
        exclude = ('top', 'submission_form', 'submission', 'published_at', 'is_final_version', 'signed_at', 'valid_until')

    def save(self, top, *args, **kwargs):
        kwargs['commit'] = False
        instance = super(SaveVoteForm, self).save(*args, **kwargs)
        instance.top = top
        instance.save()
        return instance

class VoteForm(SaveVoteForm):
    result = ResultField(required=True)

    def save(self, *args, **kwargs):
        instance = super(VoteForm, self).save(*args, **kwargs)

        if instance.result in PERMANENT_VOTE_RESULTS:
            # abort all tasks
            with sudo():
                Task.objects.for_data(instance.submission_form.submission).open().mark_deleted()

        return instance
        
class VoteReviewForm(ReadonlyFormMixin, TranslatedModelForm):
    class Meta:
        model = Vote
        fields = ('text', 'is_final_version')
        labels = {
            'is_final_version': _('Proofread and valid'),
        }

class B2VoteReviewForm(TranslatedModelForm):
    class Meta:
        model = Vote
        fields = ('text', 'is_final_version')
        labels = {
            'is_final_version': _('Proofread and valid'),
        }

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
