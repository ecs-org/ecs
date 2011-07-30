# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.contrib.auth.models import User
from django.utils.datastructures import SortedDict
from django.db.models import Count
from django.utils.translation import ugettext as _

from ecs.utils.viewutils import render, render_html, render_pdf, pdf_response
from ecs.users.utils import user_flag_required, user_group_required, sudo
from ecs.core.models import Submission, MedicalCategory, Vote, ChecklistBlueprint
from ecs.core.forms.voting import VoteForm, SaveVoteForm
from ecs.documents.models import Document
from ecs.communication.utils import send_system_message_template
from ecs.tasks.models import Task

from ecs.meetings.tasks import optimize_timetable_task
from ecs.meetings.models import Meeting, Participation, TimetableEntry, AssignedMedicalCategory, Participation
from ecs.meetings.forms import (MeetingForm, TimetableEntryForm, FreeTimetableEntryForm, UserConstraintFormSet, 
    SubmissionReschedulingForm, AssignedMedicalCategoryForm, MeetingAssistantForm, RetrospectiveThesisExpeditedVoteForm)



def create_meeting(request):
    form = MeetingForm(request.POST or None)
    if form.is_valid():
        meeting = form.save()
        return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'meetings/form.html', {
        'form': form,
    })
    
def meeting_list(request, meetings, title=None):
    if not title:
        title = _('Meetings')
    return render(request, 'meetings/list.html', {
        'meetings': meetings.order_by('start'),
        'title': title,
    })
    
def upcoming_meetings(request):
    return meeting_list(request, Meeting.objects.filter(start__gte=datetime.now()), title=_('Upcoming Meetings'))

def past_meetings(request):
    return meeting_list(request, Meeting.objects.filter(start__lt=datetime.now()), title=_('Past Meetings'))

@user_flag_required('executive_board_member')
def reschedule_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    form = SubmissionReschedulingForm(request.POST or None, submission=submission)
    if form.is_valid():
        from_meeting = form.cleaned_data['from_meeting']
        to_meeting = form.cleaned_data['to_meeting']
        old_entries = from_meeting.timetable_entries.filter(submission=submission)
        for entry in old_entries:
            to_meeting.add_entry(submission=submission, duration=entry.duration, title=entry.title, visible=(not entry.timetable_index is None))
            entry.submission = None
            entry.save()
            entry.delete() # FIXME: study gets deleted if there is a vote. We should never use delete
        return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission.current_submission_form.pk}))
    return render(request, 'meetings/reschedule.html', {
        'submission': submission,
        'form': form,
    })
    
def add_free_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    form = FreeTimetableEntryForm(request.POST or None)
    if form.is_valid():
        entry = meeting.add_entry(**form.cleaned_data)
        return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'meetings/timetable/add_free_entry.html', {
        'form': form,
        'meeting': meeting,
    })
    

def add_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    is_break = request.GET.get('break', False)
    if is_break:
        entry = meeting.add_break(duration=timedelta(minutes=30))
    else:
        entry = meeting.add_entry(duration=timedelta(minutes=7, seconds=30), submission=Submission.objects.order_by('?')[:1].get())
        import random
        for user in User.objects.order_by('?')[:random.randint(1, 4)]:
            Participation.objects.create(entry=entry, user=user)
    return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def remove_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    entry.delete()
    return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def update_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    form = TimetableEntryForm(request.POST)
    if form.is_valid():
        entry.duration = form.cleaned_data['duration']
        entry.optimal_start = form.cleaned_data['optimal_start']
        entry.save()
    return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def move_timetable_entry(request, meeting_pk=None):
    from_index = int(request.GET.get('from_index'))
    to_index = int(request.GET.get('to_index'))
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    meeting[from_index].index = to_index
    return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def users_by_medical_category(request):
    category = get_object_or_404(MedicalCategory, pk=request.POST.get('category'))
    users = list(User.objects.filter(medical_categories=category, ecs_profile__board_member=True).values('pk', 'username'))
    return HttpResponse(simplejson.dumps(users), content_type='text/json')

@user_flag_required('internal')
def timetable_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    return render(request, 'meetings/timetable/editor.html', {
        'active': 'timetable',
        'meeting': meeting,
        'running_optimization': bool(meeting.optimization_task_id),
    })

@user_flag_required('internal')
def expert_assignment(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    required_categories = MedicalCategory.objects.filter(submissions__timetable_entries__meeting=meeting).order_by('abbrev')

    forms = SortedDict()
    for cat in required_categories:
        forms[cat] = AssignedMedicalCategoryForm(request.POST or None, meeting=meeting, category=cat, prefix='cat%s' % cat.pk)

    if request.method == 'POST':
        for cat, form in forms.iteritems():
            if not form.is_valid():
                continue

            old_amc = None
            try:
                old_amc = AssignedMedicalCategory.objects.get(meeting=meeting, category=cat)
            except AssignedMedicalCategory.DoesNotExist:
                old_amc = None

            amc = form.save()

            if old_amc and old_amc.board_member and old_amc.board_member == form.cleaned_data['board_member']:
                continue

            entries = list(meeting.timetable_entries.filter(submission__medical_categories=cat).distinct())

            if old_amc and old_amc.board_member:
                # remove all participations for a previous selected board member.
                # XXX: this may delete manually entered data. (FMD2)
                Participation.objects.filter(medical_category=cat, entry__meeting=meeting).delete()

                # delete obsolete board member review tasks
                for entry in entries:
                    with sudo():
                        tasks = list(Task.objects.for_data(entry.submission).filter(task_type__workflow_node__uid='board_member_review', closed_at=None, deleted_at__isnull=True))
                    for task in tasks:
                        task.deleted_at = datetime.now()
                        task.save()

            amc = form.save()
            if amc.board_member:
                meeting.create_boardmember_reviews(send_messages=False)
                send_system_message_template(amc.board_member, _('Meeting on {date}').format(date=meeting.start.strftime('%d.%m.%Y')), 'meetings/expert_notification.txt', {
                    'category': cat,
                    'meeting': meeting,
                })

    categories = SortedDict()
    for cat in required_categories:
        try:
            categories[cat] = AssignedMedicalCategory.objects.get(meeting=meeting, category=cat).board_member
        except AssignedMedicalCategory.DoesNotExist:
            categories[cat] = None

    return render(request, 'meetings/timetable/medical_categories.html', {
        'active': 'experts',
        'meeting': meeting,
        'forms': forms,
        'categories': categories,
    })

@user_flag_required('internal')
def optimize_timetable(request, meeting_pk=None, algorithm=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.optimization_task_id:
        meeting.optimization_task_id = "xxx:fake"
        meeting.save()
        retval = optimize_timetable_task.apply_async(kwargs={'meeting_id': meeting.id, 'algorithm': algorithm})
    return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))

@user_flag_required('internal')
def edit_user_constraints(request, meeting_pk=None, user_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    user = get_object_or_404(User, pk=user_pk)
    constraint_formset = UserConstraintFormSet(request.POST or None, prefix='constraint', queryset=user.meeting_constraints.all())
    if constraint_formset.is_valid():
        for constraint in constraint_formset.save(commit=False):
            constraint.meeting = meeting
            constraint.user = user
            constraint.save()
        return HttpResponseRedirect(reverse('ecs.meetings.views.edit_user_constraints', kwargs={'meeting_pk': meeting.pk, 'user_pk': user.pk}))
    return render(request, 'meetings/constraints/user_form.html', {
        'meeting': meeting,
        'participant': user,
        'constraint_formset': constraint_formset,
    })

@user_flag_required('internal')
def meeting_assistant_quickjump(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    top = None
    q = request.REQUEST.get('q', '').upper()
    explict_top = 'TOP' in q
    q = q.replace('TOP', '').strip()
    
    # if we don't explicitly look for a TOP, try an exact ec_number lookup
    if not explict_top:
        tops = meeting.timetable_entries.filter(submission__ec_number__endswith=q).order_by('timetable_index')
        if len(tops) == 1:
            top = tops[0]
    # if we found no TOP yet, try an exact TOP index lookup
    if not top:
        try:
            top = meeting.timetable_entries.get(timetable_index=int(q)-1)
        except (ValueError, TimetableEntry.DoesNotExist):
            pass
    # if we found no TOP yet and don't explicitly look for a TOP, try a fuzzy ec_number lookup
    if not top and not explict_top:
        tops = meeting.timetable_entries.filter(submission__ec_number__icontains=q).order_by('timetable_index')
        if len(tops) == 1:
            top = tops[0]
    if top:
        return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': top.pk}))
    
    return render(request, 'meetings/assistant/quickjump_error.html', {
        'meeting': meeting,
        'tops': tops,
    })

@user_flag_required('internal')
def meeting_assistant(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if meeting.started:
        if meeting.ended:
            return render(request, 'meetings/assistant/error.html', {
                'active': 'assistant',
                'meeting': meeting,
                'message': _(u'This meeting has ended.'),
            })
        try:
            top_pk = request.session.get('meetings:%s:assistant:top_pk' % meeting.pk, None) or meeting[0].pk
            return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': top_pk}))
        except IndexError:
            return render(request, 'meetings/assistant/error.html', {
                'active': 'assistant',
                'meeting': meeting,
                'message': _(u'No TOPs are assigned to this meeting.'),
            })
    else:
        return render(request, 'meetings/assistant/error.html', {
            'active': 'assistant',
            'meeting': meeting,
            'message': _('This meeting has not yet started.'),
        })

@user_flag_required('internal')
def meeting_assistant_start(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started=None)
    meeting.started = datetime.now()
    meeting.save()
    return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))

@user_flag_required('internal')
def meeting_assistant_stop(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    if meeting.open_tops.count():
        raise Http404(_("unfinished meetings cannot be stopped"))
    meeting.ended = datetime.now()
    meeting.save()

    for k in ('retrospective_thesis_entries', 'expedited_entries', 'localec_entries'):
        tops = getattr(meeting, k).exclude(pk__in=Vote.objects.exclude(top=None).values('top__pk').query)
        for top in tops:
            vote = Vote.objects.create(top=top, result='3')
            with sudo():
                open_tasks = Task.objects.for_data(top.submission).filter(deleted_at__isnull=True, closed_at=None)
                for task in open_tasks:
                    task.deleted_at = datetime.now()
                    task.save()

            new_meeting = Meeting.objects.next_schedulable_meeting(top.submission)
            new_meeting.add_entry(submission=top.submission, duration=timedelta(minutes=7.5))

    return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))

@user_flag_required('internal')
def meeting_assistant_comments(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    form = MeetingAssistantForm(request.POST or None, instance=meeting)
    if form.is_valid():
        form.save()
        if request.POST.get('autosave', False):
            return HttpResponse('OK')
        return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'meetings/assistant/comments.html', {
        'meeting': meeting,
        'form': form,
    })

@user_flag_required('internal')
def meeting_assistant_retrospective_thesis_expedited(request, meeting_pk=None):
    from ecs.core.models.voting import FINAL_VOTE_RESULTS
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    form = RetrospectiveThesisExpeditedVoteForm(request.POST or None, meeting=meeting)
    if form.is_valid():
        form.save()
        form = RetrospectiveThesisExpeditedVoteForm(None, meeting=meeting)
    else:
        print form.errors

    return render(request, 'meetings/assistant/retrospective_thesis_expedited.html', {
        'retrospective_thesis_entries': meeting.retrospective_thesis_entries.filter(vote__result__in=FINAL_VOTE_RESULTS).order_by('submission__ec_number'),
        'expedited_entries': meeting.expedited_entries.filter(vote__result__in=FINAL_VOTE_RESULTS).order_by('submission__ec_number'),
        'localec_entries': meeting.localec_entries.filter(vote__result__in=FINAL_VOTE_RESULTS).order_by('submission__ec_number'),
        'meeting': meeting,
        'form': form,
    })

@user_flag_required('internal')
def meeting_assistant_top(request, meeting_pk=None, top_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    top = get_object_or_404(TimetableEntry, pk=top_pk)
    simple_save = request.POST.get('simple_save', False)
    autosave = request.POST.get('autosave', False)
    vote, form = None, None
    
    def next_top_redirect():
        if top.next_open:
            next_top = top.next_open
        else:
            try:
                next_top = meeting.open_tops[0]
            except IndexError:
                return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))
        return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': next_top.pk}))
    
    if top.submission:
        try:
            vote = top.vote
        except Vote.DoesNotExist:
            pass
        if simple_save:
            form_cls = SaveVoteForm
        else:
            form_cls = VoteForm
        form = form_cls(request.POST or None, instance=vote)
        if form.is_valid():
            vote = form.save(top)
            if autosave:
                return HttpResponse('OK')
            if form.cleaned_data['close_top']:
                top.is_open = False
                top.save()
            if vote.recessed:
                # schedule submission for the next schedulable meeting
                next_meeting = Meeting.objects.next_schedulable_meeting(top.submission)
                next_meeting.add_entry(submission=top.submission, duration=timedelta(minutes=7.5))
            return next_top_redirect()
    elif request.method == 'POST':
        top.is_open = False
        top.save()
        return next_top_redirect()

    last_top_cache_key = 'meetings:%s:assistant:top_pk' % meeting.pk
    last_top = None
    if last_top_cache_key in request.session:
        last_top = TimetableEntry.objects.get(pk=request.session[last_top_cache_key])
    request.session[last_top_cache_key] = top.pk
    
    checklist_review_states = SortedDict()
    if top.submission:
        for blueprint in ChecklistBlueprint.objects.order_by('name'):
            checklist_review_states[blueprint] = []
        for checklist in top.submission.checklists.select_related('blueprint'):
            checklist_review_states[checklist.blueprint].append(checklist)

    return render(request, 'meetings/assistant/top.html', {
        'meeting': meeting,
        'submission': top.submission,
        'top': top,
        'vote': vote,
        'form': form,
        'last_top': last_top,
        'checklist_review_states': checklist_review_states.items(),
    })

def agenda_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    filename = '%s-%s-%s.pdf' % (
        meeting.title, meeting.start.strftime('%d-%m-%Y'), _('agenda')
    )
    
    rts = list(meeting.retrospective_thesis_submissions.all())
    es = list(meeting.expedited_submissions.all())
    ls = list(meeting.localec_submissions.all())

    pdfstring = render_pdf(request, 'db/meetings/wkhtml2pdf/agenda.html', {
        'meeting': meeting,
        'additional_submissions': enumerate(rts + es + ls, len(meeting)+1),
    })
    return pdf_response(pdfstring, filename=filename)

@user_group_required('EC-Office')
def send_agenda_to_board(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    for recipient in settings.AGENDA_RECIPIENT_LIST:
        send_system_message_template(recipient, _('Invitation to meeting'), 'meetings/boardmember_invitation.txt', {'meeting': meeting})

    return HttpResponseRedirect(reverse('ecs.meetings.views.status', kwargs={'meeting_pk': meeting.pk}))

def protocol_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    filename = '%s-%s-%s.pdf' % (
        meeting.title, meeting.start.strftime('%d-%m-%Y'), _('protocol')
    )
    
    timetable_entries = meeting.timetable_entries.filter(timetable_index__isnull=False).order_by('timetable_index')
    tops = []
    for top in timetable_entries:
        try:
            vote = Vote.objects.filter(top=top)[0]
        except IndexError:
            vote = None
        tops.append((top, vote,))

    b2_votes = Vote.objects.filter(result='2', top__in=timetable_entries)
    submission_forms = [x.submission_form for x in b2_votes]
    b1ized = Vote.objects.filter(result='1', submission_form__in=submission_forms).order_by('submission_form__submission__ec_number')

    rts = list(meeting.retrospective_thesis_submissions.all())
    es = list(meeting.expedited_submissions.all())
    ls = list(meeting.localec_submissions.all())
    additional_submissions = []
    for i, submission in enumerate(rts + es + ls, len(tops) + 1):
        try:
            vote = Vote.objects.filter(submission_form=submission.current_submission_form)[0]
        except IndexError:
            vote = None
        additional_submissions.append((i, submission, vote,))

    pdf = render_pdf(request, 'db/meetings/wkhtml2pdf/protocol.html', {
        'meeting': meeting,
        'tops': tops,
        'b1ized': b1ized,
        'additional_submissions': additional_submissions,
    })
    return pdf_response(pdf, filename=filename)


def timetable_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    
    timetable = {}
    for entry in meeting:
        for user in entry.users:
            if user in timetable:
                timetable[user].append(entry)
            else:
                timetable[user] = [entry]
    
    timetable = sorted([{
        'user': key,
        'entries': sorted(timetable[key], key=lambda x:x.timetable_index),
    } for key in timetable], key=lambda x:x['user'])
    
    for row in timetable:
        first_entry = row['entries'][0]
        times = [{'start': first_entry.start, 'end': first_entry.end, 'index': first_entry.timetable_index}]
        for entry in row['entries'][1:]:
            if times[-1]['end'] == entry.start:
                times[-1]['end'] = entry.end
            else:
                times.append({'start': entry.start, 'end': entry.end, 'index': entry.timetable_index})
    
        row['times'] = ', '.join(['%s - %s' % (x['start'].strftime('%H:%M'), x['end'].strftime('%H:%M')) for x in times])
    
    filename = '%s-%s-%s.pdf' % (
        meeting.title, meeting.start.strftime('%d-%m-%Y'), _('time slot')
    )
    
    pdf = render_pdf(request, 'db/meetings/wkhtml2pdf/timetable.html', {
        'meeting': meeting,
        'timetable': timetable,
    })
    return pdf_response(pdf, filename=filename)

def timetable_htmlemailpart(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    response = render(request, 'meetings/email/timetable.html', {
        'meeting': meeting,
    })
    return response

def next(request):
    try:
        meeting = Meeting.objects.next()
    except Meeting.DoesNotExist:
        return HttpResponseRedirect(reverse('ecs.dashboard.views.view_dashboard'))
    else:
        return HttpResponseRedirect(reverse('ecs.meetings.views.status', kwargs={'meeting_pk': meeting.pk}))

def status(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    return render(request, 'meetings/status.html', {
        'active': 'status',
        'meeting': meeting,
    })

def votes_signing(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    tops = meeting.timetable_entries.all()
    votes_list = [ ]
    for top in tops:
        votes = Vote.objects.filter(top=top)
        c = votes.count()
        assert(c < 2)
        if c is 0:
            vote = None
        else:
            vote = votes[0]
        votes_list.append({'top_index': top.index, 'top': str(top), 'vote': vote})
    response = render(request, 'meetings/votes_signing.html', {
        'active': 'votes_signing',
        'meeting': meeting,
        'votes_list': votes_list,
    })
    return response
