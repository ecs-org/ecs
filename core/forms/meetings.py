# -*- coding: utf-8 -*
from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory

from ecs.core.models import Meeting, TimetableEntry, Constraint

from ecs.core.forms.fields import DateTimeField


class MeetingForm(forms.ModelForm):
    start = DateTimeField()
    class Meta:
        model = Meeting

class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        exclude = ('timetable_index', 'meeting', 'users', 'submission')
        

class BaseConstraintFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Constraint.objects.none())
        super(BaseConstraintFormSet, self).__init__(*args, **kwargs)

UserConstraintFormSet = modelformset_factory(Constraint, formset=BaseConstraintFormSet, extra=1, exclude = ('meeting', 'user'), can_delete=True)