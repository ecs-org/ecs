# -*- coding: utf-8 -*
from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory

from ecs.core.models import Meeting, TimeTableEntry

from ecs.core.forms.fields import DateTimeField


class MeetingForm(forms.ModelForm):
    start = DateTimeField()
    class Meta:
        model = Meeting

class TimeTableEntryForm(forms.ModelForm):
    class Meta:
        model = TimeTableEntry
        exclude = ('timetable_index', 'meeting', 'users', 'submission')