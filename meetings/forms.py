# -*- coding: utf-8 -*
from datetime import datetime

from django import forms
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from ecs.meetings.models import Meeting, TimetableEntry, Constraint, Participation, AssignedMedicalCategory, WEIGHT_CHOICES
from ecs.core.forms.fields import DateTimeField, TimeField, TimedeltaField
from ecs.votes.models import Vote
from ecs.votes.constants import FINAL_VOTE_RESULTS
from ecs.tasks.models import Task

from ecs.utils.formutils import TranslatedModelForm
from ecs.users.utils import sudo

class MeetingForm(TranslatedModelForm):
    start = DateTimeField(initial=datetime.now)
    deadline = DateTimeField(initial=datetime.now)
    deadline_diplomathesis = DateTimeField(initial=datetime.now)

    class Meta:
        model = Meeting
        exclude = ('optimization_task_id', 'submissions', 'started', 'ended', 'comments')
        labels = {
            'start': _(u'date and time'),
            'title': _(u'title'),
            'deadline': _(u'deadline'),
            'deadline_diplomathesis': _(u'deadline thesis'),
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
    weight = forms.ChoiceField(label=_(u'weighting'), choices=WEIGHT_CHOICES)

    class Meta:
        model = Constraint

UserConstraintFormSet = modelformset_factory(Constraint, formset=BaseConstraintFormSet, extra=0, exclude = ('meeting', 'user'), can_delete=True, form=ConstraintForm)

ParticipationFormSet = modelformset_factory(Participation, extra=1, can_delete=True)


class SubmissionReschedulingForm(forms.Form):
    from_meeting = forms.ModelChoiceField(Meeting.objects.none(), label=_('From meeting'))
    to_meeting = forms.ModelChoiceField(Meeting.objects.none(), label=_('To meeting'))
    
    def __init__(self, *args, **kwargs):
        submission = kwargs.pop('submission')
        super(SubmissionReschedulingForm, self).__init__(*args, **kwargs)
        current_meetings = submission.meetings.filter(started=None).order_by('start')
        self.fields['from_meeting'].queryset = current_meetings
        self.fields['to_meeting'].queryset = Meeting.objects.filter(started=None).exclude(pk__in=[m.pk for m in current_meetings]).order_by('start')


class AssignedMedicalCategoryForm(forms.ModelForm):
    class Meta:
        model = AssignedMedicalCategory
        fields = ('board_member',)

    def __init__(self, *args, **kwargs):
        instance = kwargs['instance']
        self.submissions = instance.meeting.submissions.filter(medical_categories=instance.category)
        super(AssignedMedicalCategoryForm, self).__init__(*args, **kwargs)
        self.fields['board_member'].queryset = User.objects.filter(medical_categories=instance.category, groups__name=u'EC-Board Member').order_by('email')

AssignedMedicalCategoryFormSet = modelformset_factory(AssignedMedicalCategory, extra=0, can_delete=False, form=AssignedMedicalCategoryForm)

class _EntryMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(_EntryMultipleChoiceField, self).__init__(TimetableEntry.objects, *args, **kwargs)

    def label_from_instance(self, obj):
        s = obj.submission
        return u'{0} {1}'.format(s.get_ec_number_display(), s.project_title_display())


class ExpeditedVoteForm(forms.ModelForm):
    accept_prepared_vote = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = TimetableEntry
        fields = ('accept_prepared_vote',)
        
    def has_changed(self):
        # FIXME: this should not be a model form: if no data has_changed(), save() won't be called (#3457)
        return True

    def save(self, commit=True):
        if self.cleaned_data.get('accept_prepared_vote', False):
            submission_form = self.instance.submission.current_submission_form
            vote, created = Vote.objects.get_or_create(submission_form=submission_form, defaults={'result': '1', 'is_draft': True})
            vote.top = self.instance
            vote.is_draft = False
            vote.save()
            with sudo():
                Task.objects.for_data(vote.submission_form.submission).open().mark_deleted()
            return vote
        return None

class BaseExpeditedVoteFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        queryset = kwargs.get('queryset', TimetableEntry.objects.all())
        queryset = queryset.filter(Q(vote__isnull=True) | ~Q(vote__result__in=FINAL_VOTE_RESULTS)).order_by('submission__ec_number')
        kwargs['queryset'] = queryset
        super(BaseExpeditedVoteFormSet, self).__init__(*args, **kwargs)
    
ExpeditedVoteFormSet = modelformset_factory(TimetableEntry, extra=0, can_delete=False, form=ExpeditedVoteForm, formset=BaseExpeditedVoteFormSet)
