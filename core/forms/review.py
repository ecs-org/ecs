# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ecs.core.models import Submission
from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.forms.fields import MultiselectWidget, SingleselectWidget

from ecs.utils.formutils import TranslatedModelForm

class CategorizationReviewForm(ReadonlyFormMixin, TranslatedModelForm):
    external_reviewer_name = forms.ModelChoiceField(queryset=User.objects.filter(ecs_profile__external_review=True), required=False)
    
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective', 'medical_categories', 'expedited', 'expedited_review_categories', 'external_reviewer', 'external_reviewer_name', 
            'is_amg', 'is_mpg', 'sponsor_required_for_next_meeting', 'insurance_review_required', 'gcp_review_required', 'legal_and_patient_review_required',
            'statistical_review_required', 'remission', 'keywords', 'additional_reviewers')
        labels = {
            'thesis': _('thesis'),
            'retrospective': _('retrospective'),
            'medical_categories': _('medical_categories'),
            'expedited': _('expedited'),
            'expedited_review_categories': _('expedited_review_categories'),
            'external_reviewer': _('external_reviewer'),
            'external_reviewer_name': _('external_reviewer_name'),
            'is_amg': _('is_amg'),
            'is_mpg': _('is_mpg'),
            'sponsor_required_for_next_meeting': _('sponsor_required_for_next_meeting'),
            'insurance_review_required': _('insurance_review_required'),
            'gcp_review_required': _('gcp_review_required'),
            'legal_and_patient_review_required': _('legal_and_patient_review_required'),
            'statistical_review_required': _('statistical_review_required'),
            'remission': _('remission'),
            'keywords': _('keywords'),
            'additional_reviewers': _('additional_reviewers'),
        }
        
    def __init__(self, *args, **kwargs):
        rval = super(CategorizationReviewForm, self).__init__(*args, **kwargs)
        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['medical_categories'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'medical_categories'})
            )
            self.fields['expedited_review_categories'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'expedited_review_categories'})
            )
            self.fields['additional_reviewers'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'users'})
            )
            self.fields['external_reviewer_name'].widget = SingleselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'external_reviewers'})
            )
        return rval
        
        
    def clean(self):
        from ecs.users.utils import get_user
        from django.contrib.auth.models import User

        cd = self.cleaned_data
        thesis = cd.get('thesis', None)
        expedited = cd.get('expedited', None)
        if thesis or expedited:
            cd['external_reviewer'] = False
            cd['external_reviewer_name'] = None
        return cd

class RetrospectiveThesisReviewForm(ReadonlyFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective',)


class BefangeneReviewForm(ReadonlyFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        rval = super(BefangeneReviewForm, self).__init__(*args, **kwargs)
        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['befangene'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'users'})
            )
        return rval

    class Meta:
        model = Submission
        fields = ('befangene',)
