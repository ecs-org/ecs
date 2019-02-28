from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from django.utils.translation import ugettext_lazy as _

from ecs.users.models import UserProfile
from ecs.core.models import MedicalCategory
from ecs.core.forms.fields import AutocompleteModelChoiceField, DateTimeField
from ecs.utils.formutils import require_fields
from ecs.users.utils import get_user, create_user
from ecs.users.models import LOGIN_HISTORY_TYPES
from ecs.tasks.models import TaskType


class EmailLoginForm(forms.Form):
    # Note: This has to be called "username", so we can use the django login view
    username = forms.EmailField(label=_('Email'), max_length=User._meta.get_field('email').max_length)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    error_messages = DjangoAuthenticationForm.error_messages

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        return super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': _('User')},
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class RegistrationForm(forms.Form):
    gender = forms.ChoiceField(label=_('gender'), choices=(('f', _('Ms')), ('m', _('Mr'))))
    first_name = forms.CharField(label=_('First name'))
    last_name = forms.CharField(label=_('Last name'))
    email = forms.EmailField(label=_('email'))


class ActivationForm(forms.Form):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput, min_length=8)
    password_again = forms.CharField(label=_('Password (again)'), widget=forms.PasswordInput, min_length=8)
    
    def clean_password_again(self):
        password = self.cleaned_data.get("password", "")
        if password != self.cleaned_data["password_again"]:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password

class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField()

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=User._meta.get_field('first_name').max_length,
        required=False, label=_('First Name'))
    last_name = forms.CharField(
        max_length=User._meta.get_field('last_name').max_length,
        label=_('Last Name'))
    forward_messages_after_minutes = forms.ChoiceField(choices=(
        (0, _('Never')),
        (5, _('after 5 minutes')),
        (360, _('after {0} hours').format(6)),
        (1440, _('after {0} hours').format(24)),
        (4320, _('after {0} hours').format(72)),
    ), initial=0, label=_('Forwarding of unread messages'))

    def __init__(self, *args, **kwargs):
        rval = super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['forward_messages_after_minutes'].initial = self.instance.forward_messages_after_minutes
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

        return rval

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        forward_messages_minutes = self.cleaned_data.get('forward_messages_after_minutes', 0)
        instance.forward_messages_after_minutes = int(forward_messages_minutes)
        instance.save()

        instance.user.first_name = self.cleaned_data['first_name']
        instance.user.last_name = self.cleaned_data['last_name']
        instance.user.save()

        return instance

    class Meta:
        model = UserProfile
        fields = ('gender', 'title', 'first_name', 'last_name', 'organisation', 'jobtitle',
            'address1', 'address2', 'zip_code', 'city', 'phone', 'fax', 'iban', 'swift_bic',
            'signing_connector', 'forward_messages_after_minutes',
        )
        labels = {
            'gender': _('Gender'),
            'title': _('Title'),
            'organisation': _('Organisation'),
            'jobtitle': _('Job Title'),
            'swift_bic': _('SWIFT-BIC'),
            'iban': _('IBAN'),
            'address1': _('Address/Home Address if external reviewer'),
            'address2': _('Additional Address Information'),
            'zip_code': _('ZIP-Code'),
            'city': _('City'),
            'phone': _('Phone'),
            'fax': _('Fax'),
            'signing_connector': _('Signature Environment'),
        }


class AdministrationFilterForm(forms.Form):
    activity = forms.ChoiceField(required=False, choices=(
        ('both', _('Both')),
        ('active', _('active')),
        ('inactive', _('inactive')),
    ), label=_('Activity'))
    groups = forms.ModelMultipleChoiceField(required=False,
        queryset=Group.objects.all(), label=_('Groups'))
    task_types = forms.ModelMultipleChoiceField(required=False,
        queryset=TaskType.objects
            .filter(group__name__in=('EC-Executive', 'EC-Office', 'EC-Signing'))
            .order_by('workflow_node__uid', '-pk')
            .distinct('workflow_node__uid'),
        label=_('Task Types')
    )
    medical_categories = forms.ModelMultipleChoiceField(required=False,
        queryset=MedicalCategory.objects.all(), label=_('Medical Categories'))
    keyword = forms.CharField(required=False, label=_('Name/Email'))
    page = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, data=None):
        super().__init__(data=data)

        self.fields['task_types'].choices = sorted([
            (tt.pk, '{} | {}'.format(tt.group.name, tt.trans_name))
            for tt in self.fields['task_types'].queryset
        ], key=lambda x: x[1])


class UserDetailsForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=UserProfile._meta.get_field('gender').choices, label=_('gender'))
    title = forms.CharField(max_length=UserProfile._meta.get_field('title').max_length, required=False, label=_('title'))
    first_name = forms.CharField(max_length=User._meta.get_field('first_name').max_length, label=_('First name'))
    last_name = forms.CharField(max_length=User._meta.get_field('last_name').max_length, label=_('Last name'))
    task_types = forms.ModelMultipleChoiceField(required=False,
        queryset=TaskType.objects
            .filter(group__name__in=('EC-Executive', 'EC-Office', 'EC-Signing'))
            .order_by('workflow_node__uid', '-pk')
            .distinct('workflow_node__uid'),
        label=_('Task Types')
    )
    medical_categories = forms.ModelMultipleChoiceField(
        required=False, queryset=MedicalCategory.objects.all(),
        label=_('Medical Categories'))

    class Meta:
        model = User
        fields = (
            'gender', 'title', 'first_name', 'last_name', 'groups',
            'task_types', 'medical_categories',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            profile = self.instance.profile
            self.fields['gender'].initial = profile.gender
            self.fields['title'].initial = profile.title
            self.fields['task_types'].initial = (
                self.fields['task_types'].queryset
                    .filter(workflow_node__uid__in=profile.task_uids)
                    .values_list('pk', flat=True)
            )
            self.fields['medical_categories'].initial = \
                self.instance.medical_categories.values_list('pk', flat=True)

        self.fields['task_types'].choices = sorted([
            (tt.pk, '{} | {}'.format(tt.group.name, tt.trans_name))
            for tt in self.fields['task_types'].queryset
        ], key=lambda x: x[1])

    def clean_groups(self):
        groups = self.cleaned_data.get('groups', [])
        amcs = self.instance.assigned_medical_categories.filter(meeting__ended=None)
        if amcs.exists() and not 'Specialist' in [g.name for g in groups]:
            raise forms.ValidationError(
                _('{} is a specialist in following meetings: {}').format(
                    self.instance, ', '.join(amc.meeting.title for amc in amcs))
            )
        return groups

    def clean(self):
        cd = super().clean()

        task_types = cd.get('task_types')
        if task_types:
            groups = set(cd.get('groups', []))
            for tt in task_types:
                if tt.group not in groups:
                    self.add_error('task_types',
                        _('{} requires group {}, but it is not selected').format(
                            tt.trans_name, tt.group.name))

        return cd

    def save(self):
        user = super().save()
        user.medical_categories = self.cleaned_data.get('medical_categories', ())
        profile = user.profile
        profile.gender = self.cleaned_data['gender']
        profile.title = self.cleaned_data['title']
        profile.update_flags()
        profile.task_uids = list(self.cleaned_data['task_types'].values_list(
            'workflow_node__uid', flat=True))
        profile.save()
        return user


class InvitationForm(UserDetailsForm):
    email = forms.EmailField(label=_('email'))
    invitation_text = forms.CharField(widget=forms.Textarea(), label=_('Invitation Text'))

    class Meta:
        model = User
        fields = (
            'email', 'gender', 'title', 'first_name', 'last_name', 'groups',
            'task_types', 'medical_categories', 'invitation_text',
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = get_user(email)
            raise forms.ValidationError(_('There is already a user with this email address.'))
        except User.DoesNotExist:
            pass
        return email

    def save(self):
        self.instance = create_user(self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'])
        user = super().save()
        user.profile.forward_messages_after_minutes = 5
        user.profile.save()
        return user


class IndispositionForm(forms.ModelForm):
    is_indisposed = forms.BooleanField(required=False, label=_('is_indisposed'))
    communication_proxy = AutocompleteModelChoiceField(
        'users', User.objects.all(), required=False, label=_('communication_proxy'))

    class Meta:
        model = UserProfile
        fields = ('is_indisposed', 'communication_proxy')

    def clean(self):
        cd = super().clean()

        if cd.get('is_indisposed', False):
            require_fields(self, ('communication_proxy',))

            if 'communication_proxy' in cd:
                user = self.instance.user
                proxy = cd['communication_proxy']
                proxy_chain = [user, proxy]
                while True:
                    if proxy == user:
                        self.add_error('communication_proxy',
                            _('Circular Proxy Chain: {}').format(
                                ' -> '.join(str(u) for u in proxy_chain)))
                        break
                    elif proxy.profile.is_indisposed:
                        proxy = proxy.profile.communication_proxy
                        proxy_chain.append(proxy)
                    else:
                        break

        return cd

class SetPasswordForm(DjangoSetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput, min_length=8)
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput, min_length=8)

class PasswordChangeForm(DjangoPasswordChangeForm):
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput, min_length=8)
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput, min_length=8)


class LoginHistoryFilterForm(forms.Form):
    type = forms.ChoiceField(choices=(('', '---'),) + LOGIN_HISTORY_TYPES, required=False)
    start = DateTimeField()
    end = DateTimeField()
    page = forms.IntegerField(initial=1, widget=forms.HiddenInput())

    def clean(self):
        super().clean()
        start = self.cleaned_data.get('start')
        end = self.cleaned_data.get('end')
        if start and end and start >= end:
            raise forms.ValidationError(_('Start must be before end.'))
        return self.cleaned_data
