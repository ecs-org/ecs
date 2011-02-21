# -*- coding: utf-8 -*-
from copy import deepcopy

from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from ecs.communication.models import Message, Thread
from ecs.utils.formutils import require_fields
from ecs.users.utils import get_user
from ecs.users.utils import sudo

class BaseMessageForm(forms.ModelForm):
    receiver_involved = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    receiver_person = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    receiver_type = forms.ChoiceField(choices=(('ek', _('Ethics Commission')),), widget=forms.RadioSelect(), initial='ek')
    receiver = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Message
        fields = ('text',)

    def __init__(self, submission, user, *args, **kwargs):
        super(BaseMessageForm, self).__init__(*args, **kwargs)

        receiver_type_choices = [
            ('ec', _('Ethics Commission')),
        ]
        receiver_type_initial = 'ec'

        if submission is not None:
            receiver_type_choices += [
                ('involved', _('Involved Party')),
            ]
            receiver_type_initial = 'involved'
            with sudo():
                involved_parties = list(submission.current_submission_form.get_involved_parties())
            involved_parties = User.objects.filter(pk__in=[p.user.pk for p in involved_parties if p.user])
            self.fields['receiver_involved'].queryset = involved_parties.exclude(pk=user.pk)

        if user.ecs_profile.internal:
            receiver_type_choices += [
                ('person', _('Person'))
            ]
            self.fields['receiver_person'].queryset = User.objects.exclude(pk=user.pk)

        self.fields['receiver'].queryset = User.objects.exclude(pk=user.pk)

        self.fields['receiver_type'].choices = receiver_type_choices
        self.fields['receiver_type'].initial = receiver_type_initial

    def clean_receiver(self):
        cd = self.cleaned_data

        receiver = None
        receiver_type = cd.get('receiver_type', None)

        if receiver_type == 'ec':
            receiver = get_user(settings.DEFAULT_CONTACT)
        elif receiver_type == 'involved':
            require_fields(self, ['receiver_involved',])
            receiver = cd['receiver_involved']
        elif receiver_type == 'person':
            require_fields(self, ['receiver_person',])
            receiver = cd['receiver_person']

        return receiver

class SendMessageForm(BaseMessageForm):
    subject = Thread._meta.get_field('subject').formfield()

class TaskMessageForm(BaseMessageForm):
    pass


class ReplyToMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text',)
        
class ThreadDelegationForm(forms.Form):
    to = forms.ModelChoiceField(User.objects.all())
    text = Message._meta.get_field('text').formfield()

class ThreadListFilterForm(forms.Form):
    incoming = forms.BooleanField(required=False)
    outgoing = forms.BooleanField(required=False)

