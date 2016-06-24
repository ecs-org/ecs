from datetime import timedelta

from django import forms
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from ecs.meetings.models import Meeting, TimetableEntry, Constraint, AssignedMedicalCategory, WEIGHT_CHOICES
from ecs.core.models import Submission
from ecs.core.forms.fields import DateTimeField, TimeField
from ecs.tasks.models import Task
from ecs.users.utils import sudo
from ecs.votes.models import Vote


class MeetingForm(forms.ModelForm):
    start = DateTimeField(initial=timezone.now, label=_('date and time'))
    deadline = DateTimeField(initial=timezone.now, label=_('deadline'))
    deadline_diplomathesis = DateTimeField(initial=timezone.now,
        label=_('deadline thesis'))

    class Meta:
        model = Meeting
        fields = ('start', 'title', 'deadline', 'deadline_diplomathesis')
        labels = {
            'title': _('title'),
        }

class TimetableEntryForm(forms.Form):
    duration = forms.DurationField()
    optimal_start = forms.TimeField(required=False)

class MeetingAssistantForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ('comments',)

class FreeTimetableEntryForm(forms.Form):
    title = forms.CharField(required=True, label=_('title'), max_length=TimetableEntry._meta.get_field('title').max_length)
    duration = forms.DurationField(initial='1:30:00', label=_("duration"))
    is_break = forms.BooleanField(label=_("break"), required=False)
    optimal_start = TimeField(required=False, label=_('ideal start time (time)'))
    index = forms.TypedChoiceField(label=_('Position'), coerce=int, empty_value=None, required=False, choices=[
        ('', _('Automatic')), 
        ('-1', _('Last')), 
        ('0', _('First'))
    ])

class BaseConstraintFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Constraint.objects.none())
        super(BaseConstraintFormSet, self).__init__(*args, **kwargs)

class ConstraintForm(forms.ModelForm):
    start_time = TimeField(label=_('from (time)'), required=True)
    end_time = TimeField(label=_('to (time)'), required=True)
    weight = forms.ChoiceField(label=_('weighting'), choices=WEIGHT_CHOICES)

    class Meta:
        model = Constraint
        fields = ('start_time', 'end_time', 'weight')

UserConstraintFormSet = modelformset_factory(Constraint, formset=BaseConstraintFormSet, extra=0, exclude = ('meeting', 'user'), can_delete=True, form=ConstraintForm)


class SubmissionReschedulingForm(forms.Form):
    from_meeting = forms.ModelChoiceField(Meeting.objects.none(), label=_('From meeting'), initial=0)
    to_meeting = forms.ModelChoiceField(Meeting.objects.none(), label=_('To meeting'), initial=0)
    
    def __init__(self, *args, **kwargs):
        submission = kwargs.pop('submission')
        super(SubmissionReschedulingForm, self).__init__(*args, **kwargs)
        current_meetings = submission.meetings.filter(started=None).order_by('start')
        self.fields['from_meeting'].queryset = current_meetings
        self.fields['to_meeting'].queryset = Meeting.objects.filter(started=None).exclude(pk__in=[m.pk for m in current_meetings]).order_by('start')


class UserChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        if queryset is None:
            queryset = User.objects.filter(is_active=True)
        super(UserChoiceField, self).__init__(queryset, *args, **kwargs)

    def label_from_instance(self, user):
        return '{0} <{1}>'.format(str(user), user.email)


class AssignedMedicalCategoryForm(forms.ModelForm):
    board_member = UserChoiceField(required=False)

    class Meta:
        model = AssignedMedicalCategory
        fields = ('board_member',)

    def __init__(self, *args, **kwargs):
        super(AssignedMedicalCategoryForm, self).__init__(*args, **kwargs)

        self.fields['board_member'].queryset = User.objects.filter(
            is_active=True, medical_categories=self.instance.category,
            groups__name='EC-Board Member'
        ).order_by('email')

    def _gen_submission_info(self):
        submissions = list(self.instance.meeting.submissions
            .filter(medical_categories=self.instance.category)
            .for_board_lane()
            .select_related('current_submission_form')
            .prefetch_related('biased_board_members')
            .order_by('ec_number'))

        with sudo():
            tasks = list(Task.objects.filter(
                content_type=ContentType.objects.get_for_model(Submission),
                data_id__in=[s.id for s in submissions],
                task_type__workflow_node__uid='board_member_review',
                assigned_to=self.instance.board_member,
                deleted_at=None
            ).order_by('-created_at'))

        self._submissions_in_progress = []
        self._submissions_completed = []
        self._submissions_without_review = []

        for submission in submissions:
            for task in tasks:
                if task.data == submission:
                    if task.closed_at:
                        self._submissions_completed.append(submission)
                    else:
                        self._submissions_in_progress.append(submission)
                    break
            else:
                self._submissions_without_review.append(submission)

            if self.instance.board_member in submission.biased_board_members.all():
                submission.biased = True

    @property
    def submissions_in_progress(self):
        if not hasattr(self, '_submissions_in_progress'):
            self._gen_submission_info()
        return self._submissions_in_progress

    @property
    def submissions_completed(self):
        if not hasattr(self, '_submissions_completed'):
            self._gen_submission_info()
        return self._submissions_completed

    @property
    def submissions_without_review(self):
        if not hasattr(self, '_submissions_without_review'):
            self._gen_submission_info()
        return self._submissions_without_review


AssignedMedicalCategoryFormSet = modelformset_factory(AssignedMedicalCategory,
    extra=0, can_delete=False, form=AssignedMedicalCategoryForm)


class _EntryMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(_EntryMultipleChoiceField, self).__init__(TimetableEntry.objects, *args, **kwargs)

    def label_from_instance(self, obj):
        s = obj.submission
        return '{0} {1}'.format(s.get_ec_number_display(), s.project_title_display())


class ExpeditedVoteForm(forms.ModelForm):
    accept_prepared_vote = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = TimetableEntry
        fields = ('accept_prepared_vote',)

    def __init__(self, *args, **kwargs):
        super(ExpeditedVoteForm, self).__init__(*args, **kwargs)
        if not self.instance.submission.current_submission_form.current_vote:
            self.fields['accept_prepared_vote'].initial=False
        
    def has_changed(self):
        # FIXME: this should not be a model form: if no data has_changed(), save() won't be called (#3457)
        return True

    def save(self, commit=True):
        if self.cleaned_data.get('accept_prepared_vote', False):
            submission_form = self.instance.submission.current_submission_form
            vote = submission_form.current_vote
            if vote is None:
                vote = Vote.objects.create(submission_form=submission_form, result='3a', is_draft=True)
            vote.top = self.instance
            vote.is_draft = False
            vote.save()
            self.instance.is_open = False
            self.instance.save()
            return vote
        return None

class BaseExpeditedVoteFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        queryset = kwargs.get('queryset', TimetableEntry.objects.all())
        queryset = queryset.filter(Q(vote__isnull=True) | Q(vote__is_draft=True)).order_by('submission__ec_number')
        kwargs['queryset'] = queryset
        super(BaseExpeditedVoteFormSet, self).__init__(*args, **kwargs)
    
ExpeditedVoteFormSet = modelformset_factory(TimetableEntry, extra=0, can_delete=False, form=ExpeditedVoteForm, formset=BaseExpeditedVoteFormSet)

class ExpeditedReviewerInvitationForm(forms.Form):
    start = DateTimeField(initial=lambda: timezone.now() + timedelta(days=7))


class ManualTimetableEntryCommentForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(ManualTimetableEntryCommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['class'] = 'form-control'


ManualTimetableEntryCommentFormset = modelformset_factory(TimetableEntry,
    form=ManualTimetableEntryCommentForm, extra=0)
