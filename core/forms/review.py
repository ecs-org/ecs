# -*- coding: utf-8 -*-

from django import forms
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext
from django.conf import settings

from ecs.core.models import Submission
from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.forms.fields import MultiselectWidget

class CategorizationReviewForm(ReadonlyFormMixin, forms.ModelForm):
    external_reviewer_name = forms.ModelChoiceField(queryset=User.objects.filter(ecs_profile__external_review=True), required=False)
    new_external_reviewer = forms.EmailField(required=False)
    new_additional_reviewer = forms.EmailField(required=False)
    
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective', 'medical_categories', 'expedited', 'expedited_review_categories', 'external_reviewer', 'external_reviewer_name', 
            'new_external_reviewer', 'is_amg', 'is_mpg', 'sponsor_required_for_next_meeting', 'insurance_review_required', 'gcp_review_required', 'remission',
            'keywords', 'additional_reviewers', 'new_additional_reviewer')

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
        return rval
        
        
    def clean(self):
        from ecs.users.utils import get_user
        from django.contrib.auth.models import User

        cd = self.cleaned_data
        thesis = cd.get('thesis', None)
        expedited = cd.get('expedited', None)
        new_external_reviewer = self.cleaned_data.get('new_external_reviewer', None)
        new_additional_reviewer = self.cleaned_data.get('new_additional_reviewer', None)
        if thesis or expedited:
            cd['external_reviewer'] = False
            cd['external_reviewer_name'] = None
        if new_external_reviewer:
            try:
                get_user(new_external_reviewer)
            except User.DoesNotExist:
                pass
            else:
                self._errors['new_external_reviewer'] = self.error_class([u'This user is already registered'])
        if new_additional_reviewer:
            try:
                get_user(new_additional_reviewer)
            except User.DoesNotExist:
                pass
            else:
                self._errors['new_additional_reviewer'] = self.error_class([u'This user is already registered'])
        return cd

    def save(self, request, *args, **kwargs):
        from ecs.users.utils import invite_user, get_user
        from django.contrib.auth.models import User, Group

        instance = super(CategorizationReviewForm, self).save(*args, **kwargs)
        new_external_reviewer = self.cleaned_data.get('new_external_reviewer', None)
        new_additional_reviewer = self.cleaned_data.get('new_additional_reviewer', None)

        self.data = self.data.copy()
        if new_external_reviewer:
            invite_user(request, new_external_reviewer)
            u = get_user(new_external_reviewer)
            u.ecs_profile.external_review = True
            u.ecs_profile.save()
            u.groups.add(Group.objects.get(name="External Reviewer"))
            if not instance.external_reviewer_name:
                instance.external_reviewer_name = u
                instance.save()

            self.data['external_reviewer_name'] = str(u.pk)
            self.data['new_external_reviewer'] = None

        if new_additional_reviewer:
            invite_user(request, new_additional_reviewer)
            u = get_user(new_additional_reviewer)
            instance.additional_reviewers.add(u)

            self.data['additional_reviewers'] += ',' + str(u.pk)
            self.data['new_additional_reviewer'] = None

        return instance


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


