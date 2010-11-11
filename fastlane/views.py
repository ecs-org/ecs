# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from ecs.utils.viewutils import render
from ecs.fastlane.forms import FastLaneMeetingForm, AssignedFastLaneCategoryForm
from ecs.fastlane.models import FastLaneTop, FastLaneMeeting, AssignedFastLaneCategory
from ecs.core.models import Submission

def list(request):
    meetings = FastLaneMeeting.objects.all().order_by('start')
    return render(request, 'fastlane/list.html', {
        'meetings': meetings,
    })

def new(request):
    form = FastLaneMeetingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        meeting = form.save()
        for submission in Submission.objects.next_meeting().filter(expedited=True, fast_lane_meetings__isnull=True):
            meeting.add_top(submission)

        return HttpResponseRedirect(reverse('ecs.fastlane.views.participation', kwargs={'meeting_pk': meeting.pk}))
    
    return render(request, 'fastlane/new.html', {
        'form': form,
    })

def participation(request, meeting_pk):
    meeting = get_object_or_404(FastLaneMeeting, pk=meeting_pk)

    forms = []
    for category in meeting.categories.all():
        form = AssignedFastLaneCategoryForm(request.POST or None, instance=category, prefix=category.pk)
        if request.method == 'POST' and form.is_valid():
            form.save()
            
        forms.append(form)

    return render(request, 'fastlane/participation.html', {
        'meeting': meeting,
        'forms': forms,
    })

