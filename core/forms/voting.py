# -*- coding: utf-8 -*-
from datetime import datetime

from django import forms

from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.models import Vote
from ecs.tasks.models import Task
from ecs.core.models.voting import FINAL_VOTE_RESULTS

def ResultField(**kwargs):
    return Vote._meta.get_field('result').formfield(widget=forms.RadioSelect(), **kwargs)

class SaveVoteForm(forms.ModelForm):
    result = ResultField(required=False)
    close_top = forms.BooleanField(required=False)
    executive_review_required = forms.NullBooleanField(widget=forms.HiddenInput())

    class Meta:
        model = Vote
        exclude = ('top', 'submission_form', 'submission', 'published_at', 'is_final', 'signed_at')

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

        if instance.result in FINAL_VOTE_RESULTS:
            # abort all tasks
            open_tasks = Task.objects.for_data(instance.submission_form.submission).filter(deleted_at__isnull=True, closed_at=None)
            for task in open_tasks:
                task.deleted_at = datetime.now()
                task.save()

        return instance
        
class VoteReviewForm(ReadonlyFormMixin, forms.ModelForm):
    class Meta:
        model = Vote
        fields = ('result', 'text', 'is_final')

class B2VoteReviewForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ('text', 'final', 'is_final')
