# -*- coding: utf-8 -*-

from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.utils.viewutils import render
from ecs.fastlane.forms import FastLaneMeetingForm, AssignedFastLaneCategoryForm, FastLaneTopForm
from ecs.fastlane.models import FastLaneTop, FastLaneMeeting, AssignedFastLaneCategory
from ecs.core.models import Submission
from ecs.communication.models import Thread

def list(request):
    meetings = FastLaneMeeting.objects.all().order_by('start')
    return render(request, 'fastlane/list.html', {
        'meetings': meetings,
    })

def new(request):
    form = FastLaneMeetingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        meeting = form.save()
        for submission in Submission.objects.next_meeting().filter(expedited=True, fast_lane_top__isnull=True):
            meeting.add_top(submission)

        return HttpResponseRedirect(reverse('ecs.fastlane.views.participation', kwargs={'meeting_pk': meeting.pk}))
    
    return render(request, 'fastlane/new.html', {
        'form': form,
    })

def participation(request, meeting_pk):
    meeting = get_object_or_404(FastLaneMeeting, pk=meeting_pk)

    forms = []
    for category in meeting.categories.all().order_by('pk'):
        form = AssignedFastLaneCategoryForm(request.POST or None, instance=category, prefix=category.pk)
        if request.method == 'POST' and form.is_valid():
            form.save()
            
        forms.append(form)

    return render(request, 'fastlane/participation.html', {
        'meeting': meeting,
        'forms': forms,
        'send_invitations': not meeting.categories.filter(user__isnull=True).count(),
    })

def invitations(request, meeting_pk, reallysure=False):
    meeting = get_object_or_404(FastLaneMeeting, pk=meeting_pk)

    def get_submissions_for_recipient(recipient):
        categories_q = recipient.assigned_fastlane_categories.all().values('pk').query
        return Submission.objects.filter(expedited_review_categories__pk__in=categories_q, fast_lane_meetings=meeting)

    recipients = User.objects.filter(assigned_fastlane_categories__meeting=meeting).distinct().order_by('pk')
    if reallysure:
        for recipient in recipients:
            submissions = get_submissions_for_recipient(recipient)

            text = _(u'You have been selected for the Fast Lane Meeting at %(meeting_date)s %(meeting_title)s\nas a participant to the submissions: %(submissions)s') % {
                'meeting_date': meeting.start.strftime('%d.%m.%Y %H:%M'),
                'meeting_title': meeting.title,
                'submissions': u', '.join([s.get_ec_number_display() for s in submissions])
            }
            subject = _(u'Your Participation in the Fast Lane Meeting %(meeting_date)s %(meeting_title)s') % {
                'meeting_date': meeting.start.strftime('%d.%m.%Y %H:%M'),
                'meeting_title': meeting.title,
            }
            thread, created = Thread.objects.get_or_create(
                subject=subject,
                sender=User.objects.get(username='root'),
                receiver=recipient,
            )
            thread.add_message(User.objects.get(username='root'), text=text)

        return HttpResponseRedirect(reverse('ecs.fastlane.views.list'))

    return render(request, 'fastlane/invitations.html', {
        'meeting': meeting,
        'recipients': [(x, get_submissions_for_recipient(x)) for x in recipients],
    })

def assistant(request, meeting_pk, page_num=0):
    meeting = get_object_or_404(FastLaneMeeting, pk=meeting_pk)
    page_num = int(page_num)

    paginator = Paginator(meeting.tops.all().order_by('pk'), 1)

    if not meeting.started or meeting.ended:
        return render(request, 'fastlane/assistant_main.html', {
            'meeting': meeting,
        })
    elif meeting.started and page_num not in paginator.page_range:
        return HttpResponseRedirect(reverse('ecs.fastlane.views.assistant', kwargs={'meeting_pk': meeting.pk, 'page_num': 1}))

    page = paginator.page(page_num)
    top = page.object_list[0]

    form = FastLaneTopForm(request.POST or None, instance=top)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if page_num+1 > paginator.num_pages:
            return HttpResponseRedirect(reverse('ecs.fastlane.views.assistant', kwargs={'meeting_pk': meeting.pk}))
        return HttpResponseRedirect(reverse('ecs.fastlane.views.assistant', kwargs={'meeting_pk': meeting.pk, 'page_num': page_num+1}))

    return render(request, 'fastlane/assistant_recommendation.html', {
        'meeting': meeting,
        'form': form,
        'top': top,
        'page': page,
    })

def start_assistant(request, meeting_pk):
    meeting = get_object_or_404(FastLaneMeeting, pk=meeting_pk)
    if meeting.started is not None:
        raise Http404()

    meeting.started = datetime.now()
    meeting.save()
    return HttpResponseRedirect(reverse('ecs.fastlane.views.assistant', kwargs={'meeting_pk': meeting.pk}))


def stop_assistant(request, meeting_pk):
    meeting = get_object_or_404(FastLaneMeeting, pk=meeting_pk)
    if meeting.started is None or meeting.ended is not None:
        raise Http404()

    meeting.ended = datetime.now()
    meeting.save()
    return HttpResponseRedirect(reverse('ecs.fastlane.views.assistant', kwargs={'meeting_pk': meeting.pk}))


