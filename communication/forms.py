# -*- coding: utf-8 -*-
from copy import deepcopy

from django import forms
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse

from ecs.communication.models import Message, Thread
from ecs.utils.formutils import require_fields
from ecs.users.utils import get_ec_user
from ecs.users.utils import sudo
from ecs.core.forms.fields import SingleselectWidget


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

        self.submission = submission
        self.user = user

        receiver_type_choices = [
            ('ec', '{0} ({1})'.format(force_unicode(_('Ethics Commission')), get_ec_user(submission=self.submission))),
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

        if user.get_profile().is_internal:
            receiver_type_choices += [
                ('person', _('Person'))
            ]
            self.fields['receiver_person'].queryset = User.objects.exclude(pk=user.pk)
            if getattr(settings, 'USE_TEXTBOXLIST', False):
                self.fields['receiver_person'].widget = SingleselectWidget(url=lambda: reverse('ecs.core.views.internal_autocomplete', kwargs={'queryset_name': 'users'}))

        self.fields['receiver'].queryset = User.objects.exclude(pk=user.pk)

        self.fields['receiver_type'].choices = receiver_type_choices
        self.fields['receiver_type'].initial = receiver_type_initial

    def clean_receiver(self):
        cd = self.cleaned_data

        receiver = None
        receiver_type = cd.get('receiver_type', None)

        if receiver_type == 'ec':
            receiver = get_ec_user(submission=self.submission)
        elif receiver_type == 'involved':
            require_fields(self, ['receiver_involved',])
            receiver = cd['receiver_involved']
        elif receiver_type == 'person':
            require_fields(self, ['receiver_person',])
            receiver = cd['receiver_person']

        return receiver

class SendMessageForm(BaseMessageForm):
    subject = Thread._meta.get_field('subject').formfield()

class ReplyDelegateForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(), label=_('Text'))

    def __init__(self, user, *args, **kwargs):
        super(ReplyDelegateForm, self).__init__(*args, **kwargs)
        if user.get_profile().is_internal:
            self.fields['to'] = forms.ModelChoiceField(User.objects.all(), required=False, label=_('Delegate to'))
            self.fields.keyOrder = ['to', 'text']
            if getattr(settings, 'USE_TEXTBOXLIST', False):
                self.fields['to'].widget = SingleselectWidget(url=lambda: reverse('ecs.core.views.internal_autocomplete', kwargs={'queryset_name': 'users'}))


class ThreadListFilterForm(forms.Form):
    incoming = forms.BooleanField(required=False)
    outgoing = forms.BooleanField(required=False)
    closed = forms.BooleanField(required=False)
    pending = forms.BooleanField(required=False)

