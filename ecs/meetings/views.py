from datetime import timedelta
import zipfile
import hashlib
import os
import os.path
from collections import OrderedDict

from django.conf import settings
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages

from ecs.utils.viewutils import render_html, pdf_response
from ecs.users.utils import user_flag_required, user_group_required, sudo
from ecs.core.models import Submission, MedicalCategory
from ecs.core.models.constants import SUBMISSION_TYPE_MULTICENTRIC
from ecs.checklists.models import Checklist, ChecklistBlueprint
from ecs.votes.models import Vote
from ecs.votes.forms import VoteForm, SaveVoteForm
from ecs.tasks.models import Task
from ecs.communication.mailutils import deliver

from ecs.utils.security import readonly
from ecs.meetings.tasks import optimize_timetable_task
from ecs.meetings.signals import on_meeting_start, on_meeting_end, on_meeting_top_jump, \
    on_meeting_date_changed
from ecs.meetings.models import Meeting, Participation, TimetableEntry, AssignedMedicalCategory
from ecs.meetings.forms import (MeetingForm, TimetableEntryForm, FreeTimetableEntryForm, UserConstraintFormSet,
    SubmissionReschedulingForm, AssignedMedicalCategoryFormSet, MeetingAssistantForm, ExpeditedVoteFormSet,
    ExpeditedReviewerInvitationForm, ManualTimetableEntryCommentForm, ManualTimetableEntryCommentFormset)
from ecs.communication.utils import send_system_message_template
from ecs.documents.models import Document
from ecs.meetings.cache import cache_meeting_page


@user_flag_required('is_internal')
@user_group_required('EC-Office')
def create_meeting(request):
    form = MeetingForm(request.POST or None)
    if form.is_valid():
        meeting = form.save()
        return redirect('ecs.meetings.views.meeting_details', meeting_pk=meeting.pk)
    return render(request, 'meetings/form.html', {
        'form': form,
    })

@readonly()
@user_flag_required('is_internal', 'is_resident_member')
def meeting_list(request, meetings, title=None):
    if not title:
        title = _('Meetings')
    paginator = Paginator(meetings, 12)
    try:
        meetings = paginator.page(int(request.GET.get('page', '1')))
    except (EmptyPage, InvalidPage):
        meetings = paginator.page(1)
    return render(request, 'meetings/list.html', {
        'meetings': meetings,
        'title': title,
    })

@readonly()
@user_flag_required('is_internal', 'is_resident_member')
def upcoming_meetings(request):
    return meeting_list(request, Meeting.objects.upcoming().order_by('start'), title=_('Upcoming Meetings'))

@readonly()
@user_flag_required('is_internal', 'is_resident_member')
def past_meetings(request):
    return meeting_list(request, Meeting.objects.past().order_by('-start'), title=_('Past Meetings'))

@user_flag_required('is_executive_board_member')
def reschedule_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    form = SubmissionReschedulingForm(request.POST or None, submission=submission)
    if form.is_valid():
        from_meeting = form.cleaned_data['from_meeting']
        to_meeting = form.cleaned_data['to_meeting']
        old_entries = from_meeting.timetable_entries.filter(submission=submission)

        for entry in old_entries:
            Participation.objects.filter(entry=entry).delete()
            visible = (not entry.timetable_index is None)
            entry.submission = None
            entry.save()
            entry.delete() # FIXME: study gets deleted if there is a vote. We should never use delete
            to_meeting.add_entry(submission=submission, duration=entry.duration, title=entry.title, visible=visible)
            with sudo():
                new_experts = list(AssignedMedicalCategory.objects.filter(meeting=to_meeting, board_member__isnull=False, category__pk__in=submission.medical_categories.values('pk').query).values_list('board_member__pk', flat=True))
                tasks = Task.objects.for_data(submission).filter(
                    task_type__workflow_node__uid='board_member_review').exclude(assigned_to__pk__in=new_experts).open()
                tasks.mark_deleted()
        return redirect('view_submission', submission_pk=submission.pk)
    return render(request, 'meetings/reschedule.html', {
        'submission': submission,
        'form': form,
    })

@user_flag_required('is_internal')
@cache_meeting_page(timeout=60)
def open_tasks(request, meeting=None):
    tops = list(meeting.timetable_entries.filter(submission__isnull=False).select_related('submission', 'submission__current_submission_form'))
    tops.sort(key=lambda e: e.agenda_index)

    open_tasks = OrderedDict()
    for top in tops:
        with sudo():
            ts = list(Task.objects.for_submission(top.submission).open().select_related('task_type', 'assigned_to', 'assigned_to__profile'))
        if len(ts):
            open_tasks[top] = ts
    
    return render_html(request, 'meetings/tabs/open_tasks.html', {
        'meeting': meeting,
        'open_tasks': open_tasks,
    })

@user_flag_required('is_internal')
@cache_meeting_page()
def tops(request, meeting=None):
    tops = list(meeting.timetable_entries.exclude(timetable_index=None).order_by('timetable_index').select_related('submission', 'submission__current_submission_form'))

    next_tops = [t for t in tops if t.is_open][:3]
    closed_tops = [t for t in tops if not t.is_open]

    open_tops = {}
    for top in [t for t in tops if t.is_open]:
        if top.submission:
            medical_categories = meeting.medical_categories.exclude(board_member__isnull=True).filter(
                category__in=top.submission.medical_categories.values('pk').query)
            bms = tuple(User.objects
                .filter(pk__in=medical_categories.values('board_member').query)
                .order_by('last_name', 'first_name').distinct())
        else:
            bms = ()
        if bms in open_tops:
            open_tops[bms].append(top)
        else:
            open_tops[bms] = [top]

    open_tops = OrderedDict(
        (k, open_tops[k])
        for k in sorted(open_tops.keys(),
            key=lambda us: tuple((u.last_name, u.first_name, u.id) for u in us))
    )

    return render_html(request, 'meetings/tabs/tops.html', {
        'meeting': meeting,
        'next_tops': next_tops,
        'open_tops': open_tops,
        'closed_tops': closed_tops,
    })

@user_flag_required('is_internal', 'is_board_member', 'is_resident_member')
@cache_meeting_page()
def submission_list(request, meeting=None):
    tops = list(meeting.timetable_entries.filter(timetable_index__isnull=False).order_by('timetable_index'))
    tops += list(meeting.timetable_entries.filter(timetable_index__isnull=True).order_by('pk'))
    active_top_cache_key = 'meetings:{0}:assistant:top_pk'.format(meeting.pk)
    active_top_pk = cache.get(active_top_cache_key)
    return render_html(request, 'meetings/tabs/submissions.html', {
        'meeting': meeting,
        'tops': tops,
        'active_top_pk': active_top_pk,
    })

@user_flag_required('is_internal', 'is_board_member', 'is_resident_member')
def download_zipped_documents(request, meeting_pk=None, submission_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    
    doctypes = ('patientinformation', 'checklist')
    files = set()
    
    filename_bits = [slugify(meeting.title)]

    checklist_ct = ContentType.objects.get_for_model(Checklist)
    def _add(submission):
        sf = submission.current_submission_form
        docs = sf.documents.filter(doctype__identifier__in=doctypes)
        docs |= Document.objects.filter(content_type=checklist_ct, object_id__in=Checklist.objects.filter(status='review_ok', submission=submission))
        for doc in docs.order_by('pk'):
            files.add((submission, doc))
        files.add((submission, sf.pdf_document))

    with sudo():
        if submission_pk:
            submission = get_object_or_404(meeting.submissions, pk=submission_pk)
            _add(submission)
            filename_bits.append(submission.get_filename_slice())
        else:
            for submission in meeting.submissions.order_by('pk'):
                _add(submission)

    h = hashlib.sha1()
    for submission, doc in files:
        h.update('({}:{})'.format(submission.pk, doc.pk).encode('ascii'))

    cache_file = os.path.join(settings.ECS_DOWNLOAD_CACHE_DIR, '%s.zip' % h.hexdigest())
    
    if not os.path.exists(cache_file):
        zf = zipfile.ZipFile(cache_file, 'w')
        try:
            for submission, doc in files:
                path = [submission.get_filename_slice(), doc.get_filename()]
                if not submission_pk:
                    path.insert(0, submission.get_workflow_lane_display())
                zf.writestr('/'.join(path),
                    doc.retrieve(request.user, 'meeting-zip').read())
        finally:
            zf.close()
    else:
        os.utime(cache_file, None)

    response = FileResponse(open(cache_file, 'rb'),
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="%s.ZIP"' % '_'.join(filename_bits)
    response['Content-Length'] = str(os.path.getsize(cache_file))
    return response

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def add_free_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    form = FreeTimetableEntryForm(request.POST or None)
    if form.is_valid():
        meeting.add_entry(**form.cleaned_data)
        return redirect('ecs.meetings.views.timetable_editor', meeting_pk=meeting.pk)
    return render(request, 'meetings/timetable/add_free_entry.html', {
        'form': form,
        'meeting': meeting,
    })

@user_flag_required('is_internal')
@user_group_required('EC-Office')
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
    return redirect('ecs.meetings.views.timetable_editor', meeting_pk=meeting.pk)

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def remove_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    if entry.submission:
        raise Http404(_("only tops without associated submission can be deleted"))
    entry.delete()
    return redirect('ecs.meetings.views.timetable_editor', meeting_pk=meeting.pk)

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def update_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    form = TimetableEntryForm(request.POST)
    if form.is_valid():
        entry.duration = form.cleaned_data['duration']
        entry.optimal_start = form.cleaned_data['optimal_start']
        entry.save()
        if entry.optimal_start:
            entry.move_to_optimal_position()
    return redirect('ecs.meetings.views.timetable_editor', meeting_pk=meeting.pk)

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def toggle_participation(request, meeting_pk=None, user_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    p = get_object_or_404(Participation, user=user_pk, entry=entry_pk)
    p.ignored_for_optimization = not p.ignored_for_optimization
    p.save()
    return redirect('ecs.meetings.views.timetable_editor', meeting_pk=meeting.pk)

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def move_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    from_index = int(request.GET.get('from_index'))
    to_index = int(request.GET.get('to_index'))
    meeting[from_index].index = to_index
    return redirect('ecs.meetings.views.timetable_editor', meeting_pk=meeting.pk)

@readonly()
@user_flag_required('is_internal')
@user_group_required('EC-Office')
def timetable_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    from ecs.meetings.tasks import _eval_timetable

    with sudo():
        recommendations_not_done = Task.objects.for_submissions(
            meeting.timetable_entries.filter(submission__isnull=False).values('pk')
        ).filter(task_type__workflow_node__uid__in=[
            'thesis_recommendation', 'thesis_recommendation_review',
            'expedited_recommendation', 'localec_recommendation'
        ]).open().exists()

    return render(request, 'meetings/timetable/editor.html', {
        'meeting': meeting,
        'running_optimization': bool(meeting.optimization_task_id),
        'readonly': bool(meeting.optimization_task_id) or not meeting.started is None,
        'score': _eval_timetable(meeting.metrics),
        'recommendations_not_done': recommendations_not_done,
    })

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def optimize_timetable(request, meeting_pk=None, algorithm=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.optimization_task_id:
        meeting.optimization_task_id = "xxx:fake"
        meeting.save()
        optimize_timetable_task.apply_async(kwargs={'meeting_id': meeting.id, 'algorithm': algorithm})
    return redirect('ecs.meetings.views.timetable_editor', meeting_pk=meeting.pk)

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def optimize_timetable_long(request, meeting_pk=None, algorithm=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.optimization_task_id:
        meeting.optimization_task_id = "xxx:fake"
        meeting.save()
        optimize_timetable_task.apply_async(kwargs={'meeting_id': meeting.id, 'algorithm': algorithm, 'algorithm_parameters': {
            'population_size': 400,
            'iterations': 2000,
        }})
    return redirect('ecs.meetings.views.timetable_editor', meeting_pk=meeting.pk)

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def edit_user_constraints(request, meeting_pk=None, user_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    user = get_object_or_404(User, pk=user_pk)
    formset = UserConstraintFormSet(request.POST or None, prefix='constraint', queryset=user.meeting_constraints.filter(meeting=meeting))
    if formset.is_valid():
        for constraint in formset.save(commit=False):
            constraint.meeting = meeting
            constraint.user = user
            constraint.save()
        formset = UserConstraintFormSet(None, prefix='constraint', queryset=user.meeting_constraints.filter(meeting=meeting))
        messages.success(request, _('The constraints have been saved. The constraints will be taken into account when optimizing the timetable.'))
    return render(request, 'meetings/constraints/user_form.html', {
        'meeting': meeting,
        'participant': user,
        'formset': formset,
    })

@readonly(methods=['GET'])
@user_flag_required('is_internal')
@user_group_required('EC-Office')
def meeting_assistant_quickjump(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    top = None
    q = request.GET.get('q', '').upper()
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
        return redirect('ecs.meetings.views.meeting_assistant_top', meeting_pk=meeting.pk, top_pk=top.pk)

    return render(request, 'meetings/assistant/quickjump_error.html', {
        'meeting': meeting,
        'tops': tops,
    })

@readonly()
@user_flag_required('is_internal')
@user_group_required('EC-Office')
def meeting_assistant(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if meeting.started:
        if meeting.ended:
            return render(request, 'meetings/assistant/error.html', {
                'active': 'assistant',
                'meeting': meeting,
                'message': _('This meeting has ended.'),
            })
        try:
            top_cache_key = 'meetings:{0}:assistant:top_pk'.format(meeting.pk)
            top_pk = cache.get(top_cache_key) or meeting[0].pk
            return redirect('ecs.meetings.views.meeting_assistant_top', meeting_pk=meeting.pk, top_pk=top_pk)
        except IndexError:
            return render(request, 'meetings/assistant/error.html', {
                'active': 'assistant',
                'meeting': meeting,
                'message': _('No TOPs are assigned to this meeting.'),
            })
    else:
        return render(request, 'meetings/assistant/error.html', {
            'active': 'assistant',
            'meeting': meeting,
            'message': _('This meeting has not yet started.'),
        })

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def meeting_assistant_start(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started=None)

    for top in meeting.timetable_entries.filter(submission__isnull=False):
        with sudo():
            recommendation_exists = Task.objects.for_submission(top.submission).filter(task_type__workflow_node__uid__in=['thesis_recommendation', 'thesis_recommendation_review', 'expedited_recommendation', 'localec_recommendation']).open().exists()
        if recommendation_exists:
            return render(request, 'meetings/assistant/error.html', {
                'active': 'assistant',
                'meeting': meeting,
                'message': _('There are open recommendations. You can start the meeting assistant when all recommendations are done.'),
            })
        with sudo():
            vote_preparation_exists = Task.objects.for_submission(top.submission).filter(task_type__workflow_node__uid__in=['thesis_vote_preparation', 'expedited_vote_preparation', 'localec_vote_preparation']).open().exists()
        if vote_preparation_exists:
            return render(request, 'meetings/assistant/error.html', {
                'active': 'assistant',
                'meeting': meeting,
                'message': _('There are open vote preparations. You can start the meeting assistant when all vote preparations are done.'),
            })

    meeting.started = timezone.now()
    meeting.save()
    on_meeting_start.send(Meeting, meeting=meeting)
    return redirect('ecs.meetings.views.meeting_assistant', meeting_pk=meeting.pk)

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def meeting_assistant_stop(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    if meeting.open_tops.exists():
        raise Http404(_("unfinished meetings cannot be stopped"))
    meeting.ended = timezone.now()
    meeting.save()
    on_meeting_end.send(Meeting, meeting=meeting)
    return redirect('ecs.meetings.views.meeting_assistant', meeting_pk=meeting.pk)

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def meeting_assistant_comments(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    form = MeetingAssistantForm(request.POST or None, instance=meeting)
    if form.is_valid():
        form.save()
        if request.POST.get('autosave', False):
            return HttpResponse('OK')
        return redirect('ecs.meetings.views.meeting_assistant', meeting_pk=meeting.pk)
    return render(request, 'meetings/assistant/comments.html', {
        'meeting': meeting,
        'form': form,
    })

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def meeting_assistant_retrospective_thesis_expedited(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    thesis_vote_formset = ExpeditedVoteFormSet(request.POST or None, queryset=meeting.retrospective_thesis_entries, prefix='thesis')
    expedited_vote_formset = ExpeditedVoteFormSet(request.POST or None, queryset=meeting.expedited_entries, prefix='expedited')
    localec_vote_formset = ExpeditedVoteFormSet(request.POST or None, queryset=meeting.localec_entries, prefix='localec')

    if request.method == 'POST':
        if thesis_vote_formset.is_valid():
            thesis_vote_formset.save()
            thesis_vote_formset = ExpeditedVoteFormSet(None, queryset=meeting.retrospective_thesis_entries, prefix='thesis')
        if expedited_vote_formset.is_valid():
            expedited_vote_formset.save()
            expedited_vote_formset = ExpeditedVoteFormSet(None, queryset=meeting.expedited_entries, prefix='expedited')
        if localec_vote_formset.is_valid():
            localec_vote_formset.save()
            localec_vote_formset = ExpeditedVoteFormSet(None, queryset=meeting.localec_entries, prefix='localec')

    return render(request, 'meetings/assistant/retrospective_thesis_expedited.html', {
        'retrospective_thesis_entries': meeting.retrospective_thesis_entries.filter(vote__isnull=False, vote__is_draft=False).order_by('submission__ec_number'),
        'expedited_entries': meeting.expedited_entries.filter(vote__isnull=False, vote__is_draft=False).order_by('submission__ec_number'),
        'localec_entries': meeting.localec_entries.filter(vote__isnull=False, vote__is_draft=False).order_by('submission__ec_number'),
        'meeting': meeting,
        'thesis_vote_formset': thesis_vote_formset,
        'expedited_vote_formset': expedited_vote_formset,
        'localec_vote_formset': localec_vote_formset,
    })

@readonly(methods=['GET'])
@user_flag_required('is_internal')
@user_group_required('EC-Office')
def meeting_assistant_top(request, meeting_pk=None, top_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    top = get_object_or_404(TimetableEntry, pk=top_pk)
    simple_save = request.POST.get('simple_save', False)
    autosave = request.POST.get('autosave', False)
    try:
        vote = top.vote
    except Vote.DoesNotExist:
        vote = None
    form = None

    def next_top_redirect():
        if top.next_open:
            next_top = top.next_open
        else:
            try:
                next_top = meeting.open_tops[0]
            except IndexError:
                on_meeting_top_jump.send(Meeting, meeting=meeting, timetable_entry=top)
                return redirect('ecs.meetings.views.meeting_assistant', meeting_pk=meeting.pk)
        return redirect('ecs.meetings.views.meeting_assistant_top', meeting_pk=meeting.pk, top_pk=next_top.pk)


    if top.submission and top.is_open:
        form_cls = SaveVoteForm if simple_save else VoteForm
        form = form_cls(request.POST or None, instance=vote)
        if form.is_valid():
            vote = form.save(top)
            if autosave:
                return HttpResponse('OK')
            if form.cleaned_data['close_top']:
                top.is_open = False
                top.save()
                return next_top_redirect()
            return redirect('ecs.meetings.views.meeting_assistant_top',
                meeting_pk=meeting.pk, top_pk=top.pk)
    elif top.submission and not top.is_open:
        form = VoteForm(None, instance=vote, readonly=True)
    elif not top.submission and not top.is_break:
        form = ManualTimetableEntryCommentForm(request.POST or None, instance=top)
        if form.is_valid():
            form.save()
            top.is_open = False
            top.save()
            return next_top_redirect()
    elif request.method == 'POST':
        top.is_open = False
        top.save()
        return next_top_redirect()

    last_top_cache_key = 'meetings:{0}:assistant:top_pk'.format(meeting.pk)
    last_top = None
    last_top_pk = cache.get(last_top_cache_key)
    if not last_top_pk is None:
        last_top = TimetableEntry.objects.get(pk=last_top_pk)
    cache.set(last_top_cache_key, top.pk, 60*60*24*2)
    if not last_top == top:
        on_meeting_top_jump.send(Meeting, meeting=meeting, timetable_entry=top)

    checklist_review_states = OrderedDict()
    blueprint_ct = ContentType.objects.get_for_model(ChecklistBlueprint)
    checklist_ct = ContentType.objects.get_for_model(Checklist)
    if top.submission:
        for blueprint in ChecklistBlueprint.objects.order_by('name'):
            with sudo():
                tasks = Task.objects.for_submission(top.submission).filter(deleted_at=None)
                tasks = tasks.filter(task_type__workflow_node__data_ct=blueprint_ct, task_type__workflow_node__data_id=blueprint.id
                    ) | tasks.filter(content_type=checklist_ct, data_id__in=Checklist.objects.filter(blueprint=blueprint)).exclude(workflow_token__node__uid='external_review_review')
                tasks = list(tasks.order_by('-created_at'))
            checklists = []
            for task in tasks:
                lookup_kwargs = {'blueprint': blueprint}
                if blueprint.multiple:
                    lookup_kwargs['last_edited_by'] = task.assigned_to
                try:
                    checklist = top.submission.checklists.exclude(status='dropped').filter(**lookup_kwargs)[0]
                except IndexError:
                    checklist = None
                if not checklist in [x[1] for x in checklists]:
                    checklists.append((task, checklist))
            checklists.reverse()
            checklist_review_states[blueprint] = checklists

    return render(request, 'meetings/assistant/top.html', {
        'meeting': meeting,
        'submission': top.submission,
        'top': top,
        'vote': vote,
        'form': form,
        'last_top': last_top,
        'checklist_review_states': list(checklist_review_states.items()),
    })

@readonly()
@user_flag_required('is_internal', 'is_resident_member', 'is_board_member')
def agenda_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    filename = '%s-%s-%s.pdf' % (
        slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('agenda'))
    )
    pdf = meeting.get_agenda_pdf(request)
    return pdf_response(pdf, filename=filename)

#@readonly()
@user_group_required('EC-Office')
def send_agenda_to_board(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    agenda_pdf = meeting.get_agenda_pdf(request)
    agenda_filename = '%s-%s-%s.pdf' % (slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('agenda')))
    timetable_pdf = meeting.get_timetable_pdf(request)
    timetable_filename = '%s-%s-%s.pdf' % (slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('time slot')))
    attachments = (
        (agenda_filename, agenda_pdf, 'application/pdf'),
        (timetable_filename, timetable_pdf, 'application/pdf'),
    )
    subject = _('EC Meeting %s') % (meeting.start.strftime('%d.%m.%Y'),)

    users = User.objects.filter(meeting_participations__entry__meeting=meeting).distinct()
    for user in users:
        timeframe = meeting._get_timeframe_for_user(user)
        if timeframe is None:
            continue
        start, end = timeframe
        time = '{0}–{1}'.format(start.strftime('%H:%M'), end.strftime('%H:%M'))
        htmlmail = str(render_html(request, \
                   'meetings/messages/boardmember_invitation.html', \
                   {'meeting': meeting, 'time': time, 'recipient': user, \
                    'reply_to': settings.DEFAULT_REPLY_TO}))
        deliver(user.email, subject=subject, message=None,
            message_html=htmlmail, from_email=settings.DEFAULT_FROM_EMAIL,
            rfc2822_headers={"Reply-To": settings.DEFAULT_REPLY_TO},
            attachments=attachments)

    for user in User.objects.filter(groups__name__in=settings.ECS_MEETING_AGENDA_RECEIVER_GROUPS):
        start, end = meeting.start, meeting.end
        htmlmail = str(render_html(request, \
                    'meetings/messages/resident_boardmember_invitation.html', \
                    {'meeting': meeting, 'recipient': user, \
                    'reply_to': settings.DEFAULT_REPLY_TO}))
        deliver(user.email, subject=subject, message=None,
            message_html=htmlmail, from_email=settings.DEFAULT_FROM_EMAIL,
            rfc2822_headers={"Reply-To": settings.DEFAULT_REPLY_TO},
            attachments=attachments)

    tops_with_primary_investigator = meeting.timetable_entries.filter(submission__invite_primary_investigator_to_meeting=True, submission__current_submission_form__primary_investigator__user__isnull=False, timetable_index__isnull=False)
    for top in tops_with_primary_investigator:
        sf = top.submission.current_submission_form
        for u in {sf.primary_investigator.user, sf.presenter, sf.submitter, sf.sponsor}:
            send_system_message_template(u, subject, 'meetings/messages/primary_investigator_invitation.txt', {'top': top}, submission=top.submission)

    meeting.agenda_sent_at = timezone.now()
    meeting.save()

    return redirect('ecs.meetings.views.meeting_details', meeting_pk=meeting.pk)

@readonly(methods=['GET'])
@user_group_required('EC-Office')
def send_expedited_reviewer_invitations(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    form = ExpeditedReviewerInvitationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        categories = MedicalCategory.objects.filter(submissions_for_expedited_review__in=meeting.submissions.all())
        users = User.objects.filter(profile__is_expedited_reviewer=True,
            medical_categories__in=categories.values('pk'))
        start = form.cleaned_data['start']
        for user in users:
            subject = _('Expedited Review at {0}').format(start.strftime('%d.%m.%Y'))
            send_system_message_template(user, subject, 'meetings/messages/expedited_reviewer_invitation.txt', {'start': start})
        form = ExpeditedReviewerInvitationForm(None)

        meeting.expedited_reviewer_invitation_sent_at = timezone.now()
        meeting.expedited_reviewer_invitation_sent_for = start
        meeting.save()

    return render(request, 'meetings/expedited_reviewer_invitation.html', {
        'form': form,
        'meeting': meeting,
    })


@user_group_required('EC-Office')
def edit_protocol(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, ended__isnull=False,
        protocol_sent_at=None)

    formset = ManualTimetableEntryCommentFormset(
        request.POST or None,
        prefix='protocol',
        queryset=meeting.timetable_entries.filter(submission=None, is_break=False)
    )

    if request.method == 'POST' and formset.is_valid():
        formset.save()

    return render(request, 'meetings/tabs/protocol.html', {
        'meeting': meeting,
        'formset': formset,
    })


@readonly()
@user_group_required('EC-Office')
def send_protocol(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, protocol_sent_at=None)

    meeting.protocol_sent_at = timezone.now()
    meeting.save()

    protocol_pdf = meeting.get_protocol_pdf(request)
    protocol_filename = '%s-%s-protocol.pdf' % (slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'))
    attachments = ((protocol_filename, protocol_pdf, 'application/pdf'),)
    
    for user in User.objects.filter(Q(meeting_participations__entry__meeting=meeting) | Q(groups__name__in=settings.ECS_MEETING_PROTOCOL_RECEIVER_GROUPS)).distinct():
        htmlmail = str(render_html(request, 'meetings/messages/protocol.html', {'meeting': meeting, 'recipient': user}))
        deliver(user.email, subject=_('Meeting Protocol'), message=None,
            message_html=htmlmail, from_email=settings.DEFAULT_FROM_EMAIL,
            attachments=attachments)

    return redirect('ecs.meetings.views.meeting_details', meeting_pk=meeting.pk)

@readonly()
@user_flag_required('is_internal', 'is_resident_member', 'is_board_member')
def protocol_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    filename = '%s-%s-protocol.pdf' % (slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'))
    with sudo():
        pdf = meeting.get_protocol_pdf(request)
    return pdf_response(pdf, filename=filename)

@readonly()
@user_flag_required('is_internal', 'is_resident_member', 'is_board_member')
def timetable_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    filename = '%s-%s-%s.pdf' % (
        slugify(meeting.title), meeting.start.strftime('%d-%m-%Y'), slugify(_('time slot'))
    )
    with sudo():
        pdf = meeting.get_timetable_pdf(request)
    return pdf_response(pdf, filename=filename)

@readonly()
@user_flag_required('is_internal')
def timetable_htmlemailpart(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    response = render(request, 'meetings/email/timetable.html', {
        'meeting': meeting,
    })
    return response

@readonly()
@user_flag_required('is_internal', 'is_resident_member', 'is_board_member')
def next(request):
    try:
        meeting = Meeting.objects.next()
    except Meeting.DoesNotExist:
        return redirect('ecs.dashboard.views.view_dashboard')
    else:
        return redirect('ecs.meetings.views.meeting_details', meeting_pk=meeting.pk)

@readonly(methods=['GET'])
@user_flag_required('is_internal', 'is_resident_member', 'is_board_member')
def meeting_details(request, meeting_pk=None, active=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    expert_formset = AssignedMedicalCategoryFormSet(request.POST or None, prefix='experts', queryset=AssignedMedicalCategory.objects.filter(meeting=meeting).distinct())

    if request.method == 'POST' and expert_formset.is_valid() and request.user.profile.is_internal:
        submitted_form = request.POST.get('submitted_form')
        if submitted_form == 'expert_formset' and expert_formset.is_valid():
            active = 'experts'
            messages.success(request, _('The expert assignment has been saved. The experts will be invited to the meeting when you send the agenda to the board.'))
            for amc in expert_formset.save(commit=False):
                previous_expert = AssignedMedicalCategory.objects.get(pk=amc.pk).board_member
                amc.save()
                if previous_expert == amc.board_member:
                    continue
                entries = list(meeting.timetable_entries.filter(submission__medical_categories=amc.category).distinct())
                if previous_expert:
                    # remove all participations for a previous selected board member.
                    # XXX: this may delete manually entered data. (FMD2)
                    Participation.objects.filter(medical_category=amc.category, entry__meeting=meeting, user=previous_expert).delete()

                    # delete obsolete board member review tasks
                    for entry in entries:
                        with sudo():
                            tasks = Task.objects.for_data(entry.submission).filter(
                                task_type__workflow_node__uid='board_member_review',
                                assigned_to=previous_expert).open()
                            tasks.mark_deleted()
                if amc.board_member:
                    meeting.create_boardmember_reviews()

    with sudo():
        submissions = meeting.submissions.order_by('ec_number')

    return render(request, 'meetings/details.html', {
        'cumulative_count': submissions.distinct().count(),

        'board_submissions': submissions.for_board_lane(),
        'amg_submissions': submissions.for_board_lane().amg().exclude(pk__in=meeting.submissions.mpg().values('pk').query),
        'mpg_submissions': submissions.for_board_lane().mpg().exclude(pk__in=meeting.submissions.amg().values('pk').query),
        'amg_mpg_submissions': submissions.for_board_lane().amg_mpg(),
        'not_amg_and_not_mpg_submissions': submissions.for_board_lane().not_amg_and_not_mpg(),

        'retrospective_thesis_submissions': submissions.for_thesis_lane(),
        'expedited_submissions': submissions.expedited(),
        'localec_submissions': submissions.localec(),

        'dissertation_submissions': submissions.filter(current_submission_form__project_type_education_context=1),
        'diploma_thesis_submissions': submissions.filter(current_submission_form__project_type_education_context=2),
        'amg_multi_main_submissions': submissions.amg().filter(current_submission_form__submission_type=SUBMISSION_TYPE_MULTICENTRIC),
        'billable_submissions': submissions.exclude(remission=True),
        'b3_examined_submissions': submissions.filter(pk__in=Vote.objects.filter(result='3b').values('submission_form__submission').query),
        'b3_not_examined_submissions': submissions.filter(pk__in=Vote.objects.filter(result='3a').values('submission_form__submission').query),

        'meeting': meeting,
        'expert_formset': expert_formset,
        'active': active,
    })

@user_flag_required('is_internal')
@user_group_required('EC-Office')
def edit_meeting(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    form = MeetingForm(request.POST or None, instance=meeting)
    if form.is_valid():
        meeting = form.save()
        on_meeting_date_changed.send(Meeting, meeting=meeting)
        return redirect('ecs.meetings.views.meeting_details', meeting_pk=meeting.pk)
    return render(request, 'meetings/form.html', {
        'form': form,
        'meeting': meeting,
    })
