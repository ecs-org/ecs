import datetime, random, itertools
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ecs.core.views.utils import render
from ecs.core.models import Meeting, Participation, TimetableEntry, Submission
from ecs.core.forms.meetings import MeetingForm, TimetableEntryForm, UserConstraintFormSet
from ecs.utils.timedelta import parse_timedelta
from ecs.utils.genetic_sort import GeneticSorter, inversion_mutation, swap_mutation, displacement_mutation

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
    duration = request.POST.get('duration')
    if duration:
        entry.duration = parse_timedelta(duration)
        entry.save()
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


def optimize_random(timetable, func):
    p = list(timetable)
    random.shuffle(p)
    return p
    
def optimize_brute_force(timetable, func):
    value, p = max((func(p), p) for p in itertools.permutations(timetable))
    return p
    
def optimize_ga(timetable, func):
    sorter = GeneticSorter(timetable, func, seed=(timetable,), population_size=100, crossover_p=0.3, mutations={
        inversion_mutation: 0.002,
        swap_mutation: 0.02,
        displacement_mutation: 0.01,
    })
    return sorter.run(100)

_OPTIMIZATION_ALGORITHMS = {
    'random': optimize_random,
    'brute_force': optimize_brute_force,
    'ga': optimize_ga,
}

def optimize_timetable(request, meeting_pk=None, algorithm=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    algo = _OPTIMIZATION_ALGORITHMS.get(algorithm)
    entries, users = meeting.timetable
    f = meeting.create_evaluation_func(lambda metrics: 1000*1000 * (1.0 / (metrics._waiting_time_total + 1)) + 1000.0 / (metrics.constraint_violation_total + 1))
    meeting._apply_permutation(algo(entries, f))
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
        
    