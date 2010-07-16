from django import forms
from django.forms.models import modelformset_factory
from django.contrib.auth.models import User
from ecs.core.models import Submission, TimetableEntry
from ecs.core.forms.utils import ReadonlyFormMixin

class ExecutiveReviewForm(ReadonlyFormMixin, forms.ModelForm):
    external_reviewer_name = forms.ModelChoiceField(queryset=User.objects.filter(ecs_profile__external_review=True))

    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective', 'medical_categories', 'expedited', 'expedited_review_categories',
            'external_reviewer', 'external_reviewer_name', 'sponsor_required_for_next_meeting',)


class RetrospectiveThesisReviewForm(ReadonlyFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective',)

class BefangeneReviewForm(ReadonlyFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('befangene',)


