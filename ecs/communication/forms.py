from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse

from ecs.communication.models import Message, Thread
from ecs.utils.formutils import require_fields
from ecs.users.utils import get_office_user, get_current_user
from ecs.core.forms.fields import AutocompleteModelChoiceField


class InvolvedPartiesChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(User.objects.none(), *args, **kwargs)

    def set_submission(self, submission):
        self.involved_parties = submission.current_submission_form.get_involved_parties()
        self.queryset = User.objects.filter(is_active=True, pk__in=[u.pk for u in self.involved_parties.get_users().difference([get_current_user()])])

    def label_from_instance(self, user):
        for p in self.involved_parties:
            if p.user == user:
                return '{0} ({1})'.format(user, p.involvement)
        return str(user)

class SendMessageForm(forms.ModelForm):
    subject = Thread._meta.get_field('subject').formfield()
    receiver_involved = InvolvedPartiesChoiceField(required=False)
    receiver_person = AutocompleteModelChoiceField(
        'users', User.objects.filter(is_active=True), required=False)
    receiver_type = forms.ChoiceField(
        choices=(('ek', _('Ethics Commission')),), widget=forms.RadioSelect(),
        initial='ek'
    )
    receiver = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.HiddenInput(), required=False
    )
    
    class Meta:
        model = Message
        fields = ('text',)

    def __init__(self, submission, *args, **kwargs):
        self.to_user = kwargs.pop('to', None)
        super().__init__(*args, **kwargs)

        self.submission = submission

        receiver_type_choices = [
            ('ec', '{0} ({1})'.format(ugettext('Ethics Commission'), get_office_user(submission=self.submission))),
        ]
        receiver_type_initial = 'ec'

        if submission is not None and not get_current_user() in submission.current_submission_form.get_presenting_parties():
            receiver_type_choices += [
                ('involved', _('Involved Party')),
            ]
            receiver_type_initial = 'involved'
            self.fields['receiver_involved'].set_submission(submission)

        user = get_current_user()
        if user.profile.is_internal:
            receiver_type_choices += [
                ('person', _('Person'))
            ]
            self.fields['receiver_person'].queryset = User.objects.filter(is_active=True).exclude(pk=user.pk)

        self.fields['receiver'].queryset = User.objects.filter(is_active=True).exclude(pk=user.pk)

        self.fields['receiver_type'].choices = receiver_type_choices
        self.fields['receiver_type'].initial = receiver_type_initial
        
        if self.to_user:
            self.fields['receiver_type'].required = False

    def clean_receiver(self):
        cd = self.cleaned_data
        
        if self.to_user:
            cd['receiver'] = self.to_user
            return self.to_user
        
        receiver = None
        receiver_type = cd.get('receiver_type', None)

        if receiver_type == 'ec':
            receiver = get_office_user(submission=self.submission)
        elif receiver_type == 'involved':
            require_fields(self, ['receiver_involved',])
            receiver = cd['receiver_involved']
        elif receiver_type == 'person':
            require_fields(self, ['receiver_person',])
            receiver = cd['receiver_person']

        return receiver

class ReplyDelegateForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(), label=_('Answer'))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.profile.is_internal:
            self.fields['to'] = AutocompleteModelChoiceField(
                'internal-users',
                User.objects.filter(is_active=True, profile__is_internal=True),
                required=False,
                label=_('Delegate to')
            )
            self.fields['text'] = self.fields.pop('text')       # change order


class ThreadListFilterForm(forms.Form):
    incoming = forms.BooleanField(required=False)
    outgoing = forms.BooleanField(required=False)
    closed = forms.BooleanField(required=False)
    pending = forms.BooleanField(required=False)

