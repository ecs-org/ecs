# -*- coding: utf-8 -*-

from ecs.utils.viewutils import render
from ecs.fastlane.forms import FastLaneMeetingForm

def create_fast_lane_meeting(request):
    form = FastLaneMeetingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # redirect to the schedule view
    
    return render(request, 'fastlane/create_meeting.html', {
        'form': form,
    })



