from django import forms
from django.contrib.auth.models import User
from ecs.core.models import Submission


class ExecutiveReviewForm(forms.ModelForm):
    external_reviewer_name = forms.ModelChoiceField(queryset=User.objects.filter(ecs_profile__external_review=True))

    class Meta:
        model = Submission
        fields = ('external_reviewer', 'external_reviewer_name', 'medical_categories', 'expedited', 'expedited_review_categories', 'additional_reviewers')


class RetrospectiveThesisReviewForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective')
