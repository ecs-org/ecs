# -*- coding: utf-8 -*
from datetime import datetime
from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory
from django.contrib.auth.models import User
from ecs.core.models import Meeting, TimetableEntry, Constraint, Participation, AssignedMedicalCategory
from ecs.core.forms.fields import DateTimeField, TimeField, TimedeltaField


class MeetingForm(forms.ModelForm):
    start = DateTimeField(label=u'Datum und Uhrzeit', initial=datetime.now)
    title = forms.CharField(label=u'Titel', required=False)

    class Meta:
        model = Meeting
        exclude = ('optimization_task_id', 'submissions', 'started', 'ended')

class TimetableEntryForm(forms.Form):
    duration = TimedeltaField()
    optimal_start = forms.TimeField(required=False)


class FreeTimetableEntryForm(forms.Form):
    title = forms.CharField(required=True, label=u'Titel')
    duration = TimedeltaField(initial=u'1h 30min', label=u"Dauer")
    is_break = forms.BooleanField(label=u"Pause", required=False)
    optimal_start = TimeField(required=False, label=u'Ideale Startzeit (Uhrzeit)')
    

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
    
class AssignedMedicalCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.meeting = kwargs.pop('meeting')
        self.category = kwargs.pop('category')
        self.submissions = self.meeting.submissions.filter(medical_categories=self.category)
        try:
            kwargs['instance'] = AssignedMedicalCategory.objects.get(category=self.category, meeting=self.meeting)
        except AssignedMedicalCategory.DoesNotExist:
            pass
        super(AssignedMedicalCategoryForm, self).__init__(*args, **kwargs)
        self.fields['board_member'].queryset = User.objects.filter(medical_categories=self.category).order_by('username')

    class Meta:
        model = AssignedMedicalCategory
        fields = ('board_member',)
        
    def save(self, **kwargs):
        commit = kwargs.get('commit', True)
        kwargs['commit'] = False
        obj = super(AssignedMedicalCategoryForm, self).save(**kwargs)
        obj.meeting = self.meeting
        obj.category = self.category
        if commit:
            obj.save()
        return obj
        
