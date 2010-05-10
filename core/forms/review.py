from django import forms
from ecs.core.models import Submission

class ExecutiveReviewForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('external_reviewer', 'external_reviewer_name', 'medical_categories', 'expedited', 'expedited_review_categories', 'additional_reviewers')

class RetrospectiveThesisReviewForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective')
