import datetime
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ecs.core.views.utils import render
from ecs.core.models import Meeting, Participation, TimetableEntry, Submission
from ecs.core.forms.meetings import MeetingForm, TimetableEntryForm, UserConstraintFormSet

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
        'meetings': Meeting.objects.filter(start__gte=datetime.datetime.now()).order_by('start')
    })

def add_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = meeting.add_entry(duration=datetime.timedelta(minutes=15), submission=Submission.objects.order_by('?')[:1].get())
    import random
    for user in User.objects.order_by('?')[:random.randint(1, 5)]:
        Participation.objects.create(entry=entry, user=user)
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def remove_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    entry.delete()
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def move_timetable_entry(request, meeting_pk=None):
    from_index = int(request.GET.get('from_index'))
    to_index = int(request.GET.get('to_index'))
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    meeting[from_index].index = to_index
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))

def timetable_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    return render(request, 'meetings/timetable/editor.html', {
        'meeting': meeting,
    })
    
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
        
    