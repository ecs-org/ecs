import datetime
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.contrib.auth.models import User
from ecs.core.views.utils import render
from ecs.core.models import Meeting, Participation, TimetableEntry, Submission, MedicalCategory, Participation
from ecs.core.forms.meetings import MeetingForm, TimetableEntryForm, UserConstraintFormSet, SubmissionSchedulingForm
from ecs.utils.timedelta import parse_timedelta
from ecs.core.task_queue import optimize_timetable_task

def create_meeting(request):
    form = MeetingForm(request.POST or None)
    if form.is_valid():
        meeting = form.save()
        return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'meetings/form.html', {
        'form': form,
    })
    
def meeting_list(request):
    return render(request, 'meetings/list.html', {
        #.filter(start__gte=datetime.datetime.now())
        'meetings': Meeting.objects.order_by('start')
    })
    
def schedule_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    form = SubmissionSchedulingForm(request.POST or None)
    if form.is_valid():
        kwargs = form.cleaned_data.copy()
        meeting = kwargs.pop('meeting')
        timetable_entry = meeting.add_entry(submission=submission, duration=datetime.timedelta(minutes=7.5), **kwargs)
        return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'submissions/schedule.html', {
        'submission': submission,
        'form': form,
    })

def add_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    is_break = request.GET.get('break', False)
    if is_break:
        entry = meeting.add_break(duration=datetime.timedelta(minutes=30))
    else:
        entry = meeting.add_entry(duration=datetime.timedelta(minutes=7, seconds=30), submission=Submission.objects.order_by('?')[:1].get())
        import random
        for user in User.objects.order_by('?')[:random.randint(1, 4)]:
            Participation.objects.create(entry=entry, user=user)
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def remove_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    entry.delete()
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def update_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    form = TimetableEntryForm(request.POST)
    if form.is_valid():
        duration = form.cleaned_data['duration']
        if duration:
            entry.duration = parse_timedelta(duration)
        entry.optimal_start = form.cleaned_data['optimal_start']
        entry.save()
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def move_timetable_entry(request, meeting_pk=None):
    from_index = int(request.GET.get('from_index'))
    to_index = int(request.GET.get('to_index'))
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    meeting[from_index].index = to_index
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def users_by_medical_category(request):
    category = get_object_or_404(MedicalCategory, pk=request.POST.get('category'))
    users = list(User.objects.filter(medical_categories=category).values('pk', 'username'))
    return HttpResponse(simplejson.dumps(users), content_type='text/json')

def timetable_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    return render(request, 'meetings/timetable/editor.html', {
        'meeting': meeting,
        'running_optimization': bool(meeting.optimization_task_id),
    })
    
def participation_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    users = User.objects.all()
    entries = meeting.timetable_entries.exclude(submission=None).select_related('submission')
    if request.method == 'POST':
        for entry in entries:
            for cat in entry.medical_categories:
                participations = Participation.objects.filter(entry=entry, medical_category=cat)
                user_pks = set(map(int, request.POST.getlist('users_%s_%s' % (entry.pk, cat.pk))))
                participations.exclude(user__pk__in=user_pks).delete()
                for user in User.objects.filter(pk__in=user_pks).exclude(meeting_participations__in=participations.values('pk')):
                    entry.add_user(user, cat)
            
    return render(request, 'meetings/timetable/participation_editor.html', {
        'meeting': meeting,
        'categories': MedicalCategory.objects.all(),
    })

def optimize_timetable(request, meeting_pk=None, algorithm=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.optimization_task_id:
        retval = optimize_timetable_task.delay(meeting_id=meeting.id,algorithm=algorithm)
        meeting.optimization_task_id = retval.task_id
        meeting.save()
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))

def edit_user_constraints(request, meeting_pk=None, user_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    user = get_object_or_404(User, pk=user_pk)
    constraint_formset = UserConstraintFormSet(request.POST or None, prefix='constraint', queryset=user.meeting_constraints.all())
    if constraint_formset.is_valid():
        for constraint in constraint_formset.save(commit=False):
            constraint.meeting = meeting
            constraint.user = user
            constraint.save()
        return HttpResponseRedirect(reverse('ecs.core.views.meetings.edit_user_constraints', kwargs={'meeting_pk': meeting.pk, 'user_pk': user.pk}))
    return render(request, 'meetings/constraints/user_form.html', {
        'meeting': meeting,
        'participant': user,
        'constraint_formset': constraint_formset,
    })
        
    
