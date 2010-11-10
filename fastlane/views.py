# -*- coding: utf-8 -*-

from ecs.utils.viewutils import render
from ecs.fastlane.forms import FastLaneMeetingForm
from ecs.fastlane.models import FastLaneTop
from ecs.core.models import Submission

def create_fast_lane_meeting(request):
    form = FastLaneMeetingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        meeting = form.save()
        for submission in Submission.objects.filter(expedited=True).next_meeting():
            meeting.add_top(submission)
            
        # FIXME: redirect to the next view
    
    return render(request, 'fastlane/create_meeting.html', {
        'form': form,
    })



