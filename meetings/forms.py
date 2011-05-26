# -*- coding: utf-8 -*
from datetime import datetime

from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ecs.meetings.models import Meeting, TimetableEntry, Constraint, Participation, AssignedMedicalCategory
from ecs.core.forms.fields import DateTimeField, TimeField, TimedeltaField
from ecs.core.models import Submission

from ecs.utils.formutils import TranslatedModelForm

class MeetingForm(TranslatedModelForm):
    start = DateTimeField(initial=datetime.now)
    deadline = DateTimeField(initial=datetime.now)
    deadline_diplomathesis = DateTimeField(initial=datetime.now)

    class Meta:
        model = Meeting
        exclude = ('optimization_task_id', 'submissions', 'started', 'ended')
        labels = {
            'start': _(u'date and time'),
            'title': _(u'title'),
            'deadline': _(u'deadline'),
            'deadline_diplomathesis': _(u'deadline thesis'),
            'comments': _('comments'),
        }

class TimetableEntryForm(forms.Form):
    duration = TimedeltaField()
    optimal_start = forms.TimeField(required=False)

class MeetingAssistantForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ('comments',)

class FreeTimetableEntryForm(forms.Form):
    title = forms.CharField(required=True, label=_(u'title'))
    duration = TimedeltaField(initial=u'1h 30min', label=_(u"duration"))
    is_break = forms.BooleanField(label=_(u"break"), required=False)
    optimal_start = TimeField(required=False, label=_(u'ideal start time (time)'))
    

class BaseConstraintFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Constraint.objects.none())
        super(BaseConstraintFormSet, self).__init__(*args, **kwargs)

class ConstraintForm(forms.ModelForm):
    start_time = TimeField(label=_(u'from (time)'), required=True)
    end_time = TimeField(label=_(u'to (time)'), required=True)
    weight = forms.ChoiceField(label=_(u'weighting'), choices=((0.5, _(u'unfavorable')), (1.0, _(u'impossible'))))

    class Meta:
        model = Constraint

UserConstraintFormSet = modelformset_factory(Constraint, formset=BaseConstraintFormSet, extra=0, exclude = ('meeting', 'user'), can_delete=True, form=ConstraintForm)

ParticipationFormSet = modelformset_factory(Participation, extra=1, can_delete=True)


class SubmissionReschedulingForm(forms.Form):
    from_meeting = forms.ModelChoiceField(Meeting.objects.none())
    to_meeting = forms.ModelChoiceField(Meeting.objects.none())
    
    def __init__(self, *args, **kwargs):
        submission = kwargs.pop('submission')
        super(SubmissionReschedulingForm, self).__init__(*args, **kwargs)
        now = datetime.now()
        current_meetings = submission.meetings.filter(start__gt=now).order_by('start')
        self.fields['from_meeting'].queryset = current_meetings
        self.fields['to_meeting'].queryset = Meeting.objects.filter(start__gt=now).exclude(pk__in=[m.pk for m in current_meetings])
    

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

class _SubmissionMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(_SubmissionMultipleChoiceField, self).__init__(Submission.objects, *args, **kwargs)

    def label_from_instance(self, obj):
        return u'{0} {1}'.format(obj.get_ec_number_display(), obj.project_title_display())

class RetrospectiveThesisExpeditedVoteForm(forms.Form):
    retrospective_thesis_submissions = _SubmissionMultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    expedited_submissions = _SubmissionMultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        from ecs.core.models import Vote
        from ecs.core.models.voting import FINAL_VOTE_RESULTS
        meeting = kwargs.pop('meeting')
        super(RetrospectiveThesisExpeditedVoteForm, self).__init__(*args, **kwargs)
        self.fields['retrospective_thesis_submissions'].queryset = meeting.retrospective_thesis_submissions.exclude(current_submission_form__votes__result__in=FINAL_VOTE_RESULTS).order_by('ec_number')
        self.fields['expedited_submissions'].queryset = meeting.expedited_submissions.exclude(current_submission_form__votes__result__in=FINAL_VOTE_RESULTS).order_by('ec_number')

