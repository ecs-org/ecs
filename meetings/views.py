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
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType

from ecs.utils.viewutils import render, render_html, render_pdf, pdf_response
from ecs.users.utils import user_flag_required, user_group_required, sudo
from ecs.core.models import Submission, MedicalCategory
from ecs.checklists.models import Checklist, ChecklistBlueprint
from ecs.votes.models import Vote
from ecs.votes.forms import VoteForm, SaveVoteForm
from ecs.documents.models import Document
from ecs.tasks.models import Task
from ecs.ecsmail.utils import deliver

from ecs.meetings.tasks import optimize_timetable_task
from ecs.meetings.models import Meeting, Participation, TimetableEntry, AssignedMedicalCategory, Participation
from ecs.meetings.forms import (MeetingForm, TimetableEntryForm, FreeTimetableEntryForm, UserConstraintFormSet, 
    SubmissionReschedulingForm, AssignedMedicalCategoryFormSet, MeetingAssistantForm, RetrospectiveThesisExpeditedVoteForm)



def create_meeting(request):
    form = MeetingForm(request.POST or None)
    if form.is_valid():
        meeting = form.save()
        return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_details', kwargs={'meeting_pk': meeting.pk}))
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

@user_flag_required('is_executive_board_member')
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
    if entry.submission:
        raise Http404(_("only tops without associated submission can be deleted"))
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
    users = list(User.objects.filter(medical_categories=category, ecs_profile__is_board_member=True).values('pk', 'username'))
    return HttpResponse(simplejson.dumps(users), content_type='text/json')

@user_flag_required('is_internal')
def timetable_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    return render(request, 'meetings/timetable/editor.html', {
        'meeting': meeting,
        'running_optimization': bool(meeting.optimization_task_id),
        'readonly': bool(meeting.optimization_task_id) or not meeting.started is None,
    })

@user_flag_required('is_internal')
def optimize_timetable(request, meeting_pk=None, algorithm=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.optimization_task_id:
        meeting.optimization_task_id = "xxx:fake"
        meeting.save()
        retval = optimize_timetable_task.apply_async(kwargs={'meeting_id': meeting.id, 'algorithm': algorithm})
    return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))

@user_flag_required('is_internal')
def optimize_timetable_long(request, meeting_pk=None, algorithm=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.optimization_task_id:
        meeting.optimization_task_id = "xxx:fake"
        meeting.save()
        retval = optimize_timetable_task.apply_async(kwargs={'meeting_id': meeting.id, 'algorithm': algorithm, 'algorithm_parameters': {'population_size': 1000}})
    return HttpResponseRedirect(reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))

@user_flag_required('is_internal')
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

@user_flag_required('is_internal')
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

@user_flag_required('is_internal')
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

@user_flag_required('is_internal')
def meeting_assistant_start(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started=None)
    meeting.started = datetime.now()
    meeting.save()
    return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))

@user_flag_required('is_internal')
def meeting_assistant_stop(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    if meeting.open_tops.exists():
        raise Http404(_("unfinished meetings cannot be stopped"))
    meeting.ended = datetime.now()
    meeting.save()
    for vote in Vote.objects.filter(top__meeting=meeting):
        vote.save() # trigger post_save for all votes

    for k in ('retrospective_thesis_entries', 'expedited_entries', 'localec_entries'):
        tops = getattr(meeting, k).exclude(pk__in=Vote.objects.exclude(top=None).values('top__pk').query)
        for top in tops:
            vote = Vote.objects.create(top=top, result='3a')
            with sudo():
                open_tasks = Task.objects.for_data(top.submission).filter(deleted_at__isnull=True, closed_at=None)
                for task in open_tasks:
                    task.deleted_at = datetime.now()
                    task.save()

            top.submission.schedule_to_meeting()

    return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))

@user_flag_required('is_internal')
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

@user_flag_required('is_internal')
def meeting_assistant_retrospective_thesis_expedited(request, meeting_pk=None):
    from ecs.votes.constants import FINAL_VOTE_RESULTS
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

@user_flag_required('is_internal')
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
            if vote.is_recessed:
                top.submission.schedule_to_meeting()
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
    blueprint_ct = ContentType.objects.get_for_model(ChecklistBlueprint)
    if top.submission:
        for blueprint in ChecklistBlueprint.objects.order_by('name'):
            with sudo():
                tasks = list(Task.objects.for_submission(top.submission).filter(deleted_at=None,
                    task_type__workflow_node__data_ct=blueprint_ct, task_type__workflow_node__data_id=blueprint.id))
            checklists = []
            for task in tasks:
                lookup_kwargs = {'blueprint': blueprint}
                if blueprint.multiple:
                    lookup_kwargs['user'] = task.assigned_to
                try:
                    checklist = top.submission.checklists.exclude(status='dropped').get(**lookup_kwargs)
                except Checklist.DoesNotExist:
                    checklist = None
                checklists.append((task, checklist))
            checklist_review_states[blueprint] = checklists

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
        slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('agenda'))
    )
    pdf = meeting.get_agenda_pdf(request)
    return pdf_response(pdf, filename=filename)

@user_group_required('EC-Office')
def send_agenda_to_board(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    agenda_pdf = meeting.get_agenda_pdf(request)
    agenda_filename = '%s-%s-%s.pdf' % (slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('agenda')))
    timetable_pdf = meeting.get_timetable_pdf(request)
    timetable_filename = '%s-%s-%s.pdf' % (slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('time slot')))
    attachments = ((agenda_filename, agenda_pdf, 'application/pdf'), (timetable_filename, timetable_pdf, 'application/pdf'))

    users = User.objects.filter(meeting_participations__entry__meeting=meeting).distinct()
    for user in users:
        start, end = meeting._get_timeframe_for_user(user)
        time = '{0} - {1}'.format(start.strftime('%H:%M'), end.strftime('%H:%M'))
        htmlmail = unicode(render_html(request, 'meetings/boardmember_invitation.html', {'meeting': meeting, 'time': time, 'recipient': user}))
        deliver(user.email, subject=_(u'Invitation to meeting'), message=None, message_html=htmlmail,
            from_email= settings.DEFAULT_FROM_EMAIL, attachments=attachments)

    return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_details', kwargs={'meeting_pk': meeting.pk}))

def protocol_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    filename = '%s-%s-%s.pdf' % (
        slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('protocol'))
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

    rts = list(meeting.retrospective_thesis_entries.all())
    es = list(meeting.expedited_entries.all())
    ls = list(meeting.localec_entries.all())
    additional_tops = []
    for i, top in enumerate(rts + es + ls, len(tops) + 1):
        try:
            vote = Vote.objects.filter(top=top)[0]
        except IndexError:
            vote = None
        additional_tops.append((i, top, vote,))

    pdf = render_pdf(request, 'db/meetings/wkhtml2pdf/protocol.html', {
        'meeting': meeting,
        'tops': tops,
        'b1ized': b1ized,
        'additional_tops': additional_tops,
    })
    return pdf_response(pdf, filename=filename)


def timetable_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    filename = '%s-%s-%s.pdf' % (
        slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('time slot'))
    )
    pdf = meeting.get_timetable_pdf(request)
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
        return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_details', kwargs={'meeting_pk': meeting.pk}))

@user_flag_required('is_internal')
def meeting_details(request, meeting_pk=None, active=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    required_categories = MedicalCategory.objects.filter(submissions__timetable_entries__meeting=meeting).order_by('abbrev')
    for cat in required_categories:
        AssignedMedicalCategory.objects.get_or_create(meeting=meeting, category=cat)
    expert_formset = AssignedMedicalCategoryFormSet(request.POST or None, prefix='experts', queryset=AssignedMedicalCategory.objects.filter(meeting=meeting))

    if request.method == 'POST' and expert_formset.is_valid():
        submitted_form = request.POST.get('submitted_form')
        if submitted_form == 'expert_formset' and expert_formset.is_valid():
            active = 'experts'
            for amc in expert_formset.save(commit=False):
                previous_expert = AssignedMedicalCategory.objects.get(pk=amc.pk).board_member
                amc.save()
                if previous_expert == amc.board_member:
                    continue
                entries = list(meeting.timetable_entries.filter(submission__medical_categories=amc.category).distinct())
                if previous_expert:
                    # remove all participations for a previous selected board member.
                    # XXX: this may delete manually entered data. (FMD2)
                    Participation.objects.filter(medical_category=amc.category, entry__meeting=meeting).delete()

                    # delete obsolete board member review tasks
                    for entry in entries:
                        with sudo():
                            tasks = list(Task.objects.for_data(entry.submission).filter(
                                task_type__workflow_node__uid='board_member_review', closed_at=None, deleted_at__isnull=True))
                        for task in tasks:
                            task.deleted_at = datetime.now()
                            task.save()
                if amc.board_member:
                    meeting.create_boardmember_reviews()

    open_tasks = {}
    for submission in meeting.submissions.all():
        with sudo():
            ts = list(Task.objects.for_submission(submission).filter(closed_at__isnull=True, deleted_at__isnull=True))
        if len(ts):
            open_tasks[submission] = ts

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

    board_members = meeting.medical_categories.exclude(board_member__isnull=True).values('board_member').distinct().values_list('board_member', flat=True)
    tops_without_votes = []
    for bm in board_members:
        amcs = meeting.medical_categories.filter(board_member=bm).order_by('category__abbrev')
        tops = list(meeting.timetable_entries.filter(submission__medical_categories__pk__in=[amc.category.pk for amc in amcs], vote__isnull=True).order_by('timetable_index'))
        if tops:
            tops_without_votes.append({'board_member': amcs[0].board_member, 'amcs': amcs, 'tops': tops})
    tops = meeting.timetable_entries.filter(vote__isnull=True, submission__isnull=False).exclude(submission__medical_categories__pk__in=meeting.medical_categories.exclude(board_member__isnull=True).values('category__pk').query)
    if tops:
        tops_without_votes.append({'board_member': None, 'amcs': None, 'tops': tops})

    tops_with_votes = meeting.timetable_entries.exclude(vote__isnull=True)

    return render(request, 'meetings/details.html', {
        'cumulative_count': meeting.submissions.all().count(),
        'amg_count': meeting.submissions.amg().exclude(pk__in=meeting.submissions.mpg().values('pk').query).count(),
        'mpg_count': meeting.submissions.mpg().exclude(pk__in=meeting.submissions.amg().values('pk').query).count(),
        'amg_mpg_count': meeting.submissions.amg_mpg().count(),
        'retrospective_thesis_count': meeting.submissions.retrospective_thesis().count(),
        'expedited_count': meeting.submissions.expedited().count(),
        'localec_count': meeting.submissions.localec().count(),
        'other_count': meeting.submissions.exclude(pk__in=meeting.submissions.amg().values('pk').query).exclude(pk__in=meeting.submissions.mpg().values('pk').query).exclude(pk__in=meeting.submissions.retrospective_thesis().values('pk').query).exclude(pk__in=meeting.submissions.expedited().values('pk').query).exclude(pk__in=meeting.submissions.localec().values('pk').query).count(),
        'dissertation_count': meeting.submissions.filter(current_submission_form__project_type_education_context=1).count(),
        'diploma_thesis_count': meeting.submissions.filter(current_submission_form__project_type_education_context=2).count(),
        'amg_multi_main_count': meeting.submissions.localec().count(),
        'remission_count': meeting.submissions.filter(remission=True).count(),
        'b3_examined_count': Vote.objects.filter(result='3b', top__meeting__pk=meeting.pk).count(),
        'b3_not_examined_count': Vote.objects.filter(result='3a', top__meeting__pk=meeting.pk).count(),
        'meeting': meeting,
        'expert_formset': expert_formset,
        'open_tasks': open_tasks,
        'votes_list': votes_list,
        'tops_without_votes': tops_without_votes,
        'tops_with_votes': tops_with_votes,
        'active': active,
    })


@user_flag_required('is_internal')
def edit_meeting(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    form = MeetingForm(request.POST or None, instance=meeting)
    if form.is_valid():
        meeting = form.save()
        return HttpResponseRedirect(reverse('ecs.meetings.views.meeting_details', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'meetings/form.html', {
        'form': form,
        'meeting': meeting,
    })

def votes_signing(request, meeting_pk=None):
    return meeting_details(request, meeting_pk=meeting_pk, active='signing')
