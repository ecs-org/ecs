# -*- coding: utf-8 -*
from datetime import datetime
from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory
from django.contrib.auth.models import User
from ecs.core.models import Meeting, TimetableEntry, Constraint, Participation
from ecs.core.forms.fields import DateTimeField, TimeField


class MeetingForm(forms.ModelForm):
    start = DateTimeField(label=u'Datum und Uhrzeit', initial=datetime.now)
    title = forms.CharField(label=u'Titel', required=False)

    class Meta:
        model = Meeting
        exclude = ('optimization_task_id', 'submissions')

class TimetableEntryForm(forms.Form):
    duration = forms.CharField(required=False)
    optimal_start = forms.TimeField(required=False)


class BaseConstraintFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Constraint.objects.none())
        super(BaseConstraintFormSet, self).__init__(*args, **kwargs)
        
class ConstraintForm(forms.ModelForm):
    start_time = TimeField(label=u'Von (Uhrzeit)', required=True)
    end_time = TimeField(label=u'Bis (Uhrzeit)', required=True)
    weight = forms.ChoiceField(label=u'Gewichtung', choices=((0.5, u'ungünstig'), (1.0, u'unmöglich')))

    class Meta:
        model = Constraint

UserConstraintFormSet = modelformset_factory(Constraint, formset=BaseConstraintFormSet, extra=0, exclude = ('meeting', 'user'), can_delete=True, form=ConstraintForm)

ParticipationFormSet = modelformset_factory(Participation, extra=1, can_delete=True)

class SubmissionSchedulingForm(forms.Form):
    meeting = forms.ModelChoiceField(Meeting.objects.all())
    title = forms.CharField(required=False)
    sponsor_invited = forms.BooleanField(required=False)
    