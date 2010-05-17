from django import forms
from django.forms.models import modelformset_factory
from django.contrib.auth.models import User
from ecs.core.models import Submission, TimetableEntry, ChecklistBlueprint, Checklist, ChecklistAnswer, ChecklistQuestion


class ExecutiveReviewForm(forms.ModelForm):
    external_reviewer_name = forms.ModelChoiceField(queryset=User.objects.filter(ecs_profile__external_review=True))

    class Meta:
        model = Submission
        fields = ('external_reviewer', 'external_reviewer_name', 'medical_categories', 
            'expedited', 'expedited_review_categories', 'additional_reviewers', 'sponsor_required_for_next_meeting')


class RetrospectiveThesisReviewForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective')


class ChecklistStatisticsReviewForm(forms.ModelForm):
    class Meta:
        model = Checklist
        #fields = ('blueprint')
