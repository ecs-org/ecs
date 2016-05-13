from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from ecs.core.models import Submission
from ecs.core.models.constants import SUBMISSION_LANE_BOARD, SUBMISSION_LANE_EXPEDITED
from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.forms.fields import AutocompleteModelMultipleChoiceField, BooleanWidget
from ecs.utils.formutils import require_fields
from ecs.users.utils import get_current_user


class CategorizationReviewForm(ReadonlyFormMixin, forms.ModelForm):
    external_reviewers = AutocompleteModelMultipleChoiceField(
        'external-reviewers', User.objects, required=False,
        label=_('external_reviewers'))

    class Meta:
        model = Submission
        fields = ('workflow_lane', 'medical_categories', 'remission',
            'legal_and_patient_review_required', 'statistical_review_required', 'insurance_review_required',
            'gcp_review_required', 'invite_primary_investigator_to_meeting', 'external_reviewers')
        widgets = {
            'remission': BooleanWidget,
            'legal_and_patient_review_required': BooleanWidget,
            'statistical_review_required': BooleanWidget,
            'insurance_review_required': BooleanWidget,
            'gcp_review_required': BooleanWidget,
        }
        labels = {
            'workflow_lane': _('workflow lane'),
            'medical_categories': _('medical_categories'),
            'remission': _('remission'),
            'legal_and_patient_review_required': _('legal_and_patient_review_required'),
            'statistical_review_required': _('statistical_review_required'),
            'insurance_review_required': _('insurance_review_required'),
            'gcp_review_required': _('gcp_review_required'),
            'invite_primary_investigator_to_meeting': _('invite_primary_investigator_to_meeting'),
        }

    def __init__(self, *args, **kwargs):
        super(CategorizationReviewForm, self).__init__(*args, **kwargs)
        try:
            submission = self.instance
            submission_form = submission.current_submission_form
            user = get_current_user()
            if not user.profile.is_internal or user in submission_form.get_presenting_parties().get_users().union([submission.presenter, submission.susar_presenter]):
                del self.fields['external_reviewers']
        except AttributeError:
            pass        # workaround for old docstashes; remove in 2013 when no old docstashes are left

    def clean(self):
        cd = self.cleaned_data
        lane = cd.get('workflow_lane')
        if lane in (SUBMISSION_LANE_BOARD, SUBMISSION_LANE_EXPEDITED):
            require_fields(self, ('medical_categories',))
        if lane != SUBMISSION_LANE_BOARD:
            cd['invite_primary_investigator_to_meeting'] = False
        return cd


class BefangeneReviewForm(ReadonlyFormMixin, forms.ModelForm):
    befangene = AutocompleteModelMultipleChoiceField(
        'board-members', User.objects, required=False)

    class Meta:
        model = Submission
        fields = ('befangene',)
