# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.users.models import UserProfile
from ecs.core.models import MedicalCategory, ExpeditedReviewCategory
from ecs.core.forms.fields import MultiselectWidget


email_length = User._meta.get_field('email').max_length

class EmailLoginForm(forms.Form):
    # Note: This has to be called "username", so we can use the django login view
    username = forms.EmailField(label=_('Email'), max_length=email_length)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        return super(EmailLoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_('Please enter a correct email and password. Note that the password is case-sensitive.'))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_('This account is inactive.'))
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                _("Your Web browser doesn't appear to have cookies enabled. "
                "Cookies are required for logging in."))

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class RegistrationForm(forms.Form):
    gender = forms.ChoiceField(choices=(('f', _(u'Ms')), ('m', _(u'Mr'))))
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()


class ActivationForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password_again = forms.CharField(widget=forms.PasswordInput)
    
    def clean_password_again(self):
        password = self.cleaned_data.get("password", "")
        if password != self.cleaned_data["password_again"]:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password

class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField()


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        rval = super(ProfileForm, self).__init__(*args, **kwargs)

        forward_messages_initial = '0'
        if self.instance:
            forward_messages_initial = str(self.instance.forward_messages_after_minutes)

        self.fields['forward_messages_after_minutes'] = forms.ChoiceField(required=False, choices=(
            ('0', _(u'Never forward unread messages')),
            ('5', _(u'Forward unread messages after 5 minutes')),
            ('10', _(u'Forward unread messages after 10 minutes')),
            ('360', _(u'Forward unread messages after 6 hours')),
        ), initial=forward_messages_initial)

        return rval

    def save(self, *args, **kwargs):
        instance = super(ProfileForm, self).save(*args, **kwargs)

        forward_messages_minutes = self.cleaned_data.get('forward_messages_after_minutes', '0')
        instance.forward_messages_after_minutes = int(forward_messages_minutes)
        instance.save()

        return instance
        

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
    activity = forms.ChoiceField(required=False, choices=(
        ('both', _(u'Both')),
        ('active', _(u'active')),
        ('inactive', _(u'inactive')),
    ))
    group = forms.ModelChoiceField(required=False, queryset=Group.objects.all())
    page = forms.CharField(required=False, widget=forms.HiddenInput())
    keyword = forms.CharField(required=False)

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('groups',)

    def __init__(self, *args, **kwargs):
        rval = super(UserDetailsForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.ecs_profile.board_member:
            self.fields['medical_categories'] = forms.ModelMultipleChoiceField(
                required=False,
                queryset=MedicalCategory.objects.all(),
                initial=[x.pk for x in self.instance.medical_categories.all()],
            )
            self.fields['expedited_review_categories'] = forms.ModelMultipleChoiceField(
                required=False,
                queryset=ExpeditedReviewCategory.objects.all(),
                initial=[x.pk for x in self.instance.expedited_review_categories.all()],
            )

        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['groups'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'groups'})
            )
            if self.instance and self.instance.ecs_profile.board_member:
                self.fields['medical_categories'].widget = MultiselectWidget(
                    url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'medical_categories'})
                )
                self.fields['expedited_review_categories'].widget = MultiselectWidget(
                    url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'expedited_review_categories'})
                )

        return rval

    def save(self, *args, **kwargs):
        instance = super(UserDetailsForm, self).save(*args, **kwargs)
        instance.medical_categories = self.cleaned_data.get('medical_categories', ())
        instance.expedited_review_categories = self.cleaned_data.get('expedited_review_categories', ())
        instance.save()
        return instance

class ProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('external_review', 'board_member', 'executive_board_member', 'thesis_review', 'insurance_review', 'expedited_review', 'internal', 'help_writer')

class InvitationForm(forms.Form):
    email = forms.EmailField()

