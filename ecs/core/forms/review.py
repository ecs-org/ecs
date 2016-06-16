from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from ecs.core.models import Submission
from ecs.core.models.constants import SUBMISSION_LANE_BOARD, SUBMISSION_LANE_EXPEDITED
from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.forms.fields import AutocompleteModelMultipleChoiceField, BooleanWidget
from ecs.utils.formutils import require_fields


class CategorizationReviewForm(ReadonlyFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = (
            'workflow_lane', 'medical_categories', 'remission',
            'invite_primary_investigator_to_meeting',
        )
        widgets = {
            'remission': BooleanWidget,
        }
        labels = {
            'workflow_lane': _('workflow lane'),
            'medical_categories': _('medical_categories'),
            'remission': _('remission'),
            'invite_primary_investigator_to_meeting': _('invite_primary_investigator_to_meeting'),
        }

    def clean(self):
        cd = self.cleaned_data
        lane = cd.get('workflow_lane')
        if lane in (SUBMISSION_LANE_BOARD, SUBMISSION_LANE_EXPEDITED):
            require_fields(self, ('medical_categories',))
        if lane != SUBMISSION_LANE_BOARD:
            cd['invite_primary_investigator_to_meeting'] = False
        return cd


class BiasedBoardMembersReviewForm(forms.Form):
    biased_board_members = AutocompleteModelMultipleChoiceField(
        'board-members', User.objects, required=False)
