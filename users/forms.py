# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from ecs.users.models import UserProfile
from ecs.core.models import MedicalCategory, ExpeditedReviewCategory
from ecs.core.forms.fields import MultiselectWidget

class RegistrationForm(forms.Form):
    gender = forms.ChoiceField(choices=(('f', _(u'Ms')), ('m', _(u'Mr'))))
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()


class ActivationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_again = forms.CharField(widget=forms.PasswordInput)
    
    def clean_password_again(self):
        password = self.cleaned_data.get("password", "")
        if password != self.cleaned_data["password_again"]:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password

class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('gender', 'title', 'organisation', 'jobtitle', 'swift_bic', 'iban',
            'address1', 'address2', 'zip_code', 'city', 'phone', 'fax', 'social_security_number',
        )
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class AdministrationFilterForm(forms.Form):
    approval = forms.ChoiceField(required=False, choices=(
        ('both', _(u'Both')),
        ('yes', _(u'Approved')),
        ('no', _(u'Not Approved')),
    ))
    group = forms.ModelChoiceField(required=False, queryset=Group.objects.all())
    page = forms.CharField(required=False, widget=forms.HiddenInput())

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('groups',)
        widgets = {
            'groups': MultiselectWidget(url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'groups'})),
        }

    def __init__(self, *args, **kwargs):
        rval = super(UserDetailsForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.ecs_profile.board_member:
            self.fields['medical_categories'] = forms.ModelMultipleChoiceField(
                required=False,
                queryset=MedicalCategory.objects.all(),
                widget=MultiselectWidget(url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'medical_categories'})),
                initial=[x.pk for x in self.instance.medical_categories.all()],
            )
            self.fields['expedited_review_categories'] = forms.ModelMultipleChoiceField(
                required=False,
                queryset=ExpeditedReviewCategory.objects.all(),
                widget=MultiselectWidget(url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'expedited_review_categories'})),
                initial=[x.pk for x in self.instance.expedited_review_categories.all()],
            )
        return rval

    def save(self, *args, **kwargs):
        instance = super(UserDetailsForm, self).save(*args, **kwargs)
        instance.medical_categories = self.cleaned_data['medical_categories']
        instance.expedited_review_categories = self.cleaned_data['expedited_review_categories']
        instance.save()
        return instance

class ProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('external_review', 'board_member', 'executive_board_member', 'thesis_review', 'insurance_review', 'expedited_review', 'internal')

class InvitationForm(forms.Form):
    email = forms.EmailField()

