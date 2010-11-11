# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from ecs.utils.viewutils import render
from ecs.fastlane.forms import FastLaneMeetingForm, AssignedFastLaneCategoryForm, FastLaneTopForm
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

def assistant(request, meeting_pk, page_num=1):
    meeting = get_object_or_404(FastLaneMeeting, pk=meeting_pk)
    page_num = int(page_num)

    paginator = Paginator(meeting.tops.all(), 1)
    page = paginator.page(page_num)
    top = page.object_list[0]

    form = FastLaneTopForm(request.POST or None, instance=top)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('ecs.fastlane.views.assistant', kwargs={'meeting_pk': meeting.pk, 'page_num': page_num+1}))
        

    return render(request, 'fastlane/assistant.html', {
        'meeting': meeting,
        'form': form,
        'top': top,
        'page': page,
    })

