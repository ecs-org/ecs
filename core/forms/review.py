# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ecs.core.models import Submission
from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.forms.fields import MultiselectWidget, SingleselectWidget

from ecs.utils.formutils import TranslatedModelForm, require_fields

def _unpickle(f, args, kwargs):
    return globals()[f.replace('FormFormSet', 'FormSet')](*args, **kwargs)

class CategorizationReviewForm(ReadonlyFormMixin, TranslatedModelForm):
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective', 'medical_categories', 'expedited', 'expedited_review_categories',
            'is_amg', 'is_mpg', 'sponsor_required_for_next_meeting', 'insurance_review_required', 'gcp_review_required', 'legal_and_patient_review_required',
            'statistical_review_required', 'remission', 'external_reviewers')
        labels = {
            'thesis': _('thesis'),
            'retrospective': _('retrospective'),
            'medical_categories': _('medical_categories'),
            'expedited': _('expedited'),
            'expedited_review_categories': _('expedited_review_categories'),
            'is_amg': _('is_amg'),
            'is_mpg': _('is_mpg'),
            'sponsor_required_for_next_meeting': _('sponsor_required_for_next_meeting'),
            'insurance_review_required': _('insurance_review_required'),
            'gcp_review_required': _('gcp_review_required'),
            'legal_and_patient_review_required': _('legal_and_patient_review_required'),
            'statistical_review_required': _('statistical_review_required'),
            'remission': _('remission'),
            'external_reviewers': _('external_reviewers'),
        }

    def __reduce__(self):
        return (_unpickle, (self.__class__.__name__, (), {'data': self.data or None, 'prefix': self.prefix, 'initial': self.initial}))

    def __init__(self, *args, **kwargs):
        super(CategorizationReviewForm, self).__init__(*args, **kwargs)
        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['medical_categories'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'medical_categories'})
            )
            self.fields['expedited_review_categories'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'expedited_review_categories'})
            )
            self.fields['external_reviewers'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.internal_autocomplete', kwargs={'queryset_name': 'users'})
            )

    def clean(self):
        cd = self.cleaned_data
        if cd['expedited']:
            require_fields(self, ('expedited_review_categories',))
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
                url=lambda: reverse('ecs.core.views.internal_autocomplete', kwargs={'queryset_name': 'users'})
            )
        return rval

    class Meta:
        model = Submission
        fields = ('befangene',)
