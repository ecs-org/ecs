# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ecs.core.models import Submission
from ecs.core.models.constants import SUBMISSION_LANE_BOARD, SUBMISSION_LANE_EXPEDITED
from ecs.core.forms.utils import ReadonlyFormMixin, NewReadonlyFormMixin
from ecs.core.forms.fields import MultiselectWidget, BooleanWidget
from ecs.utils.formutils import ModelFormPickleMixin, TranslatedModelForm, require_fields
from ecs.users.utils import get_current_user

class CategorizationReviewForm(ModelFormPickleMixin, NewReadonlyFormMixin, TranslatedModelForm):
    class Meta:
        model = Submission
        fields = ('workflow_lane', 'medical_categories', 'expedited_review_categories', 'remission',
            'legal_and_patient_review_required', 'statistical_review_required', 'insurance_review_required',
            'gcp_review_required', 'invite_primary_investigator_to_meeting', 'external_reviewers', 'executive_comment')
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
            'expedited_review_categories': _('expedited_review_categories'),
            'remission': _('remission'),
            'legal_and_patient_review_required': _('legal_and_patient_review_required'),
            'statistical_review_required': _('statistical_review_required'),
            'insurance_review_required': _('insurance_review_required'),
            'gcp_review_required': _('gcp_review_required'),
            'invite_primary_investigator_to_meeting': _('invite_primary_investigator_to_meeting'),
            'external_reviewers': _('external_reviewers'),
            'executive_comment': _('executive_comment'),
        }

    def __init__(self, *args, **kwargs):
        super(CategorizationReviewForm, self).__init__(*args, **kwargs)

        try:
            submission = self.instance
            submission_form = submission.current_submission_form
            user = get_current_user()
            if not user.get_profile().is_internal or user in submission_form.get_presenting_parties().get_users().union([submission.presenter, submission.susar_presenter]):
                del self.fields['external_reviewers']
        except AttributeError:
            pass        # workaround for old docstashes; remove in 2013 when no old docstashes are left

        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['medical_categories'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'medical_categories'})
            )
            self.fields['expedited_review_categories'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'expedited_review_categories'})
            )
            if 'external_reviewers' in self.fields.keys():
                self.fields['external_reviewers'].widget = MultiselectWidget(
                    url=lambda: reverse('ecs.core.views.internal_autocomplete', kwargs={'queryset_name': 'users'})
                )

    def clean(self):
        cd = self.cleaned_data
        lane = cd.get('workflow_lane')
        if lane == SUBMISSION_LANE_BOARD:
            require_fields(self, ('medical_categories',))
        elif lane == SUBMISSION_LANE_EXPEDITED:
            require_fields(self, ('expedited_review_categories',))
        if lane != SUBMISSION_LANE_BOARD:
            cd['invite_primary_investigator_to_meeting'] = False
        return cd


class BefangeneReviewForm(ReadonlyFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        rval = super(BefangeneReviewForm, self).__init__(*args, **kwargs)
        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['befangene'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.internal_autocomplete', kwargs={'queryset_name': 'users'})
            )
        return rval

    class Meta:
        model = Submission
        fields = ('befangene',)
