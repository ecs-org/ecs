# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User, Group

from ecs.users.models import UserProfile
from ecs.core.models import MedicalCategory, ExpeditedReviewCategory

class RegistrationForm(forms.Form):
    gender = forms.ChoiceField(choices=(('f', 'Frau'), ('m', 'Herr')))
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
        ('both', 'Both'),
        ('yes', 'Approved'),
        ('no', 'Not Approved'),
    ))
    group = forms.ModelChoiceField(required=False, queryset=Group.objects.all())

class UserDetailsForm(forms.ModelForm):
    medical_categories = forms.ModelMultipleChoiceField(required=False, queryset=MedicalCategory.objects.all())
    expedited_review_categories = forms.ModelMultipleChoiceField(required=False, queryset=ExpeditedReviewCategory.objects.all())
    class Meta:
        model = User
        fields = ('groups',)

class ProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('approved_by_office',)


