import os
import tempfile
import re
from itertools import groupby

from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse, FileResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import Q, Prefetch, Min, F
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages

from ecs.documents.models import Document
from ecs.documents.views import handle_download
from ecs.utils.viewutils import redirect_to_next_url
from ecs.core.models import (
    Submission, SubmissionForm, Investigator, TemporaryAuthorization,
    MedicalCategory, EthicsCommission,
)
from ecs.checklists.models import ChecklistBlueprint, Checklist
from ecs.meetings.models import Meeting

from ecs.core.forms import (
    SubmissionFormForm, MeasureFormSet, RoutineMeasureFormSet,
    NonTestedUsedDrugFormSet, ParticipatingCenterNonSubjectFormSet,
    ForeignParticipatingCenterFormSet, InvestigatorFormSet,
    InvestigatorEmployeeFormSet, TemporaryAuthorizationForm,
    SubmissionImportForm, SubmissionFilterForm, SubmissionMinimalFilterForm,
    PresenterChangeForm, SusarPresenterChangeForm,
    AssignedSubmissionsFilterForm, AllSubmissionsFilterForm,
)
from ecs.core.forms.review import CategorizationForm, BiasedBoardMemberForm
from ecs.core.forms.layout import SUBMISSION_FORM_TABS
from ecs.votes.forms import VoteReviewForm, VotePreparationForm, B2VotePreparationForm
from ecs.core.forms.utils import submission_form_to_dict
from ecs.checklists.forms import ChecklistAnswerFormSet
from ecs.notifications.models import (
    Notification, NotificationType, CenterCloseNotification,
    AmendmentNotification, SafetyNotification, NotificationAnswer,
)

from ecs.core.workflow import ChecklistReview

from ecs.core.signals import on_study_submit, on_presenter_change, on_susar_presenter_change
from ecs.core.serializer import Serializer
from ecs.docstash.decorators import with_docstash
from ecs.docstash.models import DocStash
from ecs.votes.models import Vote
from ecs.core.diff import diff_submission_forms
from ecs.communication.utils import send_message_template
from ecs.utils import forceauth
from ecs.users.models import UserProfile
from ecs.users.utils import sudo, user_flag_required, get_user
from ecs.tasks.models import Task
from ecs.tasks.utils import get_obj_tasks, task_required, with_task_management

from ecs.documents.views import upload_document, delete_document


def get_submission_formsets(data=None, initial=None, readonly=False):
    formset_classes = [
        ('measure', MeasureFormSet),
        ('routinemeasure', RoutineMeasureFormSet),
        ('nontesteduseddrug', NonTestedUsedDrugFormSet),
        ('participatingcenternonsubject', ParticipatingCenterNonSubjectFormSet),
        ('foreignparticipatingcenter', ForeignParticipatingCenterFormSet),
        ('investigator', InvestigatorFormSet),
        ('investigatoremployee', InvestigatorEmployeeFormSet),
    ]
    formsets = {}
    for name, formset_cls in formset_classes:
        kwargs = {
            'prefix': name,
            'readonly': readonly,
            'initial': initial.get(name) if initial else None,
        }
        if readonly:
            kwargs['extra'] = 0
        formsets[name] = formset_cls(data, **kwargs)
    return formsets


def get_submission_formsets_initial(instance):
    formset_initializers = [
        ('measure', lambda sf: sf.measures.filter(category='6.1')),
        ('routinemeasure', lambda sf: sf.measures.filter(category='6.2')),
        ('nontesteduseddrug', lambda sf: sf.nontesteduseddrug_set.all()),
        ('participatingcenternonsubject', lambda sf: sf.participatingcenternonsubject_set.all()),
        ('foreignparticipatingcenter', lambda sf: sf.foreignparticipatingcenter_set.all()),
        ('investigator', lambda sf: sf.investigators.all()),
    ]
    formsets = {}
    for name, initial in formset_initializers:
        formsets[name] = [
            model_to_dict(obj, exclude=('id',))
            for obj in initial(instance).order_by('id')
        ]

    initial = []
    if instance:
        for index, investigator in enumerate(instance.investigators.order_by('id')):
            for employee in investigator.employees.order_by('id'):
                employee_dict = model_to_dict(employee, exclude=('id', 'investigator'))
                employee_dict['investigator_index'] = index
                initial.append(employee_dict)
    formsets['investigatoremployee'] = initial
    return formsets


def copy_submission_form(request, submission_form_pk=None, notification_type_pk=None, delete=False):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk, submission__presenter=request.user)

    if delete:
        docstash = DocStash.objects.create(
            group='ecs.core.views.submissions.create_submission_form',
            owner=request.user,
        )
        created = True
    else:
        for docstash in DocStash.objects.filter(group='ecs.notifications.views.create_notification', owner=request.user):
            sf_id = docstash.get('extra', {}).get('old_submission_form_id')
            if sf_id and docstash['type_id'] == notification_type_pk:
                sf = SubmissionForm.objects.get(id=sf_id)
                if sf.submission == submission_form.submission:
                    return redirect('ecs.notifications.views.create_notification',
                        docstash_key=docstash.key,
                        notification_type_pk=notification_type_pk)

        docstash, created = DocStash.objects.get_or_create(
            group='ecs.core.views.submissions.create_submission_form',
            owner=request.user,
            content_type=ContentType.objects.get_for_model(Submission),
            object_id=submission_form.submission.pk,
        )

    if created:
        docstash.name = submission_form.german_project_title

        initial = get_submission_formsets_initial(submission_form)
        initial['submission_form'] = submission_form_to_dict(submission_form)
        docstash.value = {
            'initial': initial,
            'document_pks': list(submission_form.documents.values_list('pk', flat=True)),
        }
        if not delete:
            docstash['submission_id'] = submission_form.submission.id

    if notification_type_pk:
        docstash['notification_type_id'] = notification_type_pk
    docstash.save()

    if delete:
        submission_form.submission.delete()

    return redirect('ecs.core.views.submissions.create_submission_form',
        docstash_key=docstash.key)


def copy_latest_submission_form(request, submission_pk=None, **kwargs):
    submission = get_object_or_404(Submission, pk=submission_pk)
    kwargs['submission_form_pk'] = submission.newest_submission_form.pk
    return redirect('ecs.core.views.submissions.copy_submission_form', **kwargs)


def view_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    return redirect('readonly_submission_form', submission_form_pk=submission.current_submission_form.pk)


def readonly_submission_form(request, submission_form_pk=None, submission_form=None, extra_context=None, template='submissions/readonly_form.html', checklist_overwrite=None):
    if not submission_form:
        submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = SubmissionFormForm(initial=submission_form_to_dict(submission_form), readonly=True)
    formsets = get_submission_formsets(
        initial=get_submission_formsets_initial(submission_form),
        readonly=True)
    submission = submission_form.submission

    crumbs_key = 'submission_breadcrumbs-user_{0}'.format(request.user.pk)
    crumbs = cache.get(crumbs_key, [])
    crumbs = ([submission.pk] + [pk for pk in crumbs if not pk == submission.pk])[:3]
    cache.set(crumbs_key, crumbs, 60*60*24*30) # store for thirty days

    checklists_q = Q(last_edited_by=request.user)
    if request.user.profile.is_internal:
        checklists_q |= Q(status__in=['completed', 'review_ok'])
    else:
        checklists_q |= Q(status__in=['completed', 'review_ok']) & ~(Q(blueprint__slug='external_review') & ~Q(status='review_ok'))
    checklists = submission.checklists.filter(checklists_q).order_by('blueprint__name')

    checklist_reviews = []
    for checklist in checklists:
        if checklist_overwrite and checklist in checklist_overwrite:
            checklist_formset = checklist_overwrite[checklist]
        else:
            checklist_formset = ChecklistAnswerFormSet(None, readonly=True,
                prefix='checklist{}'.format(checklist.id),
                queryset=checklist.answers.order_by('question__index'))

            task = (get_obj_tasks((ChecklistReview,), submission, data=checklist.blueprint)
                .filter(assigned_to=request.user, deleted_at=None)
                .exclude(task_type__workflow_node__uid='thesis_recommendation_review')  # XXX: legacy
                .order_by('-closed_at')
                .first())

            if task and task.closed_at and (
                task.task_type.workflow_node.uid not in (
                    'thesis_recommendation', 'expedited_recommendation',
                    'localec_recommendation',
                ) or submission.meetings.filter(started=None).exists()
            ):
                checklist_formset.allow_reopen = True
        checklist_reviews.append((checklist, checklist_formset))

    checklist_summary = []
    for checklist in checklists:
        if checklist.is_negative or checklist.get_all_answers_with_comments().exists():
            q = Q(question__is_inverted=False, answer=False) | Q(question__is_inverted=True, answer=True)
            q |= Q(question__requires_comment=False) & ~(Q(comment=None) | Q(comment=''))
            answers = checklist.answers.filter(q)
            checklist_summary.append((checklist, answers))

    submission_forms = list(
        submission.forms(manager='unfiltered').only(
            'submission_id', 'is_acknowledged', 'presenter_id', 'created_at',
            'is_notification_update', 'pdf_document_id',

            'presenter__first_name', 'presenter__last_name', 'presenter__email',
        ).prefetch_related(
            Prefetch('new_for_notification', queryset=
                AmendmentNotification.objects.only('new_submission_form_id')),
            Prefetch('presenter__profile', queryset=
                UserProfile.objects.only('gender', 'title', 'user_id')),
        ).order_by('-created_at')
    )
    for sf, prev in zip(submission_forms, submission_forms[1:]):
        sf.previous_form = prev
    current_form_idx = [sf.id == submission.current_submission_form_id for sf in submission_forms].index(True)

    external_review_checklists = submission.checklists.filter(blueprint__slug='external_review')
    notifications = (submission.notifications
        .only(
            'timestamp', 'type_id',

            'user__first_name', 'user__last_name', 'user__email',
        )
        .select_related('type')
        .prefetch_related(
            Prefetch('user__profile', queryset=
                UserProfile.objects.only('gender', 'title', 'user_id')),
            Prefetch('safetynotification', queryset=
                SafetyNotification.objects.only('safety_type')),
            Prefetch('answer', queryset=
                NotificationAnswer.objects
                    .only('notification_id', 'is_rejected')
            ),
        )
        .order_by('-timestamp'))
    votes = submission.votes

    current_docstash = DocStash.objects.filter(
        group='ecs.core.views.submissions.create_submission_form',
        owner=request.user,
        content_type=ContentType.objects.get_for_model(Submission),
        object_id=submission.id,
    ).only('key', 'owner', 'modtime').first()
    
    stashed_notifications = []
    for d in DocStash.objects.filter(owner=request.user, group='ecs.notifications.views.create_notification'):
        if not d.POST:
            continue

        submission_form_pks = d.POST.getlist('submission_forms',
            d.POST.getlist('submission_form', []))
        if any(str(sf.pk) in submission_form_pks for sf in submission_forms):
            stashed_notifications.append(d)

    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'documents': submission_form.documents
            .select_related('doctype')
            .order_by('doctype__identifier', 'date', 'name'),
        'readonly': True,
        'submission': submission,
        'submission_form': submission_form,
        'submission_forms': submission_forms,
        'current_form_idx': current_form_idx,
        'checklist_reviews': checklist_reviews,
        'checklist_summary': checklist_summary,
        'open_notifications': notifications.pending(),
        'answered_notifications': notifications.exclude(pk__in=Notification.objects.pending().values('pk').query),
        'stashed_notifications': stashed_notifications,
        'pending_votes': votes.filter(published_at=None),
        'published_votes': votes.filter(published_at__isnull=False),
        'diff_notification_types': NotificationType.objects.filter(includes_diff=True).order_by('name'),
        'external_review_checklists': external_review_checklists,
        'temporary_auth': submission.temp_auth.order_by('end'),
        'temporary_auth_form': TemporaryAuthorizationForm(prefix='temp_auth'),
        'current_docstash': current_docstash,
    }

    center_close_notifications = CenterCloseNotification.objects.filter(
        answer__published_at__isnull=False, answer__is_rejected=False,
        investigator__submission_form__submission_id=submission.id
    ).annotate(
        organisation=F('investigator__organisation'),
        ethics_commission_id=F('investigator__ethics_commission_id')
    ).values('organisation', 'ethics_commission_id', 'close_date')
    for form in formsets['investigator']:
        for n in center_close_notifications:
            if n['organisation'] == form.initial['organisation'] and \
                n['ethics_commission_id'] == form.initial['ethics_commission']:
                form.close_date = n['close_date']
                break

    presenting_users = submission_form.get_presenting_parties().get_users().union([submission.presenter, submission.susar_presenter])
    if not request.user in presenting_users:
        vote = submission.current_pending_vote or submission.current_published_vote
        context['vote_review_form'] = VoteReviewForm(instance=vote, readonly=True)
        context['categorization_form'] = CategorizationForm(instance=submission, readonly=True)
        if request.user.profile.is_executive and \
            submission.allows_categorization():
            task = Task.unfiltered.for_data(submission).filter(
                task_type__workflow_node__uid='categorization',
                deleted_at=None,
            ).order_by('-closed_at').first()
            if task and task.closed_at:
                context['categorization_form'].allow_reopen = True

    if not submission_form == submission.newest_submission_form:
        context['unacknowledged_forms'] = submission.forms.filter(pk__gt=submission_form.pk).count()

    if extra_context:
        context.update(extra_context)

    for prefix, formset in formsets.items():
        context['%s_formset' % prefix] = formset
    return render(request, template, context)


def submission_form_pdf(request, submission_form_pk=None, view=False):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    return handle_download(request, submission_form.pdf_document, view=view)


def submission_form_pdf_view(request, submission_form_pk=None):
    return submission_form_pdf(request, submission_form_pk, view=True)


def submission_form_pdf_debug(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    response = HttpResponse(submission_form.render_pdf(),
        content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=debug.pdf'
    return response


def download_document(request, submission_form_pk=None, document_pk=None, view=False):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    document = get_object_or_404(submission_form.documents, pk=document_pk)
    return handle_download(request, document, view=view)


def view_document(request, submission_form_pk=None, document_pk=None):
    return download_document(request, submission_form_pk, document_pk, view=True)


@task_required
@with_task_management
def categorization(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    task = request.task_management.task

    docstash, created = DocStash.objects.get_or_create(
        group='ecs.core.views.submissions.categorization',
        owner=request.user,
        content_type=ContentType.objects.get_for_model(task.__class__),
        object_id=task.pk,
    )

    form = CategorizationForm(request.POST or docstash.POST, instance=submission)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            docstash.delete()
        else:
            docstash.POST = request.POST
            docstash.save()

    response = readonly_submission_form(request,
        submission_form=submission.current_submission_form,
        extra_context={'categorization_form': form,})
    response.has_errors = not form.is_valid()
    return response


@user_flag_required('is_executive')
def reopen_categorization(request, submission_pk=None):
    submission = get_object_or_404(Submission.unfiltered.select_for_update(),
        pk=submission_pk)

    task = Task.unfiltered.for_data(submission).filter(
        task_type__workflow_node__uid='categorization',
        deleted_at=None,
    ).order_by('-closed_at').first()

    if not task or not task.closed_at or not submission.allows_categorization():
        raise Http404()

    new_task = task.reopen(request.user)

    if task.assigned_to != request.user:
        sender = get_user('root@system.local')
        subject = _('{task} reopened').format(task=task.task_type)
        send_message_template(sender, task.assigned_to, subject,
            'tasks/messages/reopen.txt', {'user': request.user, 'task': task},
            submission=submission, reply_receiver=request.user)

    return redirect(new_task.url)


def reopen_checklist(request, submission_pk=None, blueprint_pk=None):
    submission = get_object_or_404(
        Submission.unfiltered.filter(
            pk__in=Submission.objects.filter(pk=submission_pk).values('pk')
        ).select_for_update()
    )
    blueprint = get_object_or_404(ChecklistBlueprint, pk=blueprint_pk)

    task = (get_obj_tasks((ChecklistReview,), submission, data=blueprint)
        .filter(assigned_to=request.user, deleted_at=None)
        .exclude(task_type__workflow_node__uid='thesis_recommendation_review')  # XXX: legacy
        .order_by('-closed_at')
        .first())

    if not task or not task.closed_at or (
        task.task_type.workflow_node.uid in (
            'thesis_recommendation', 'expedited_recommendation',
            'localec_recommendation',
        ) and not submission.meetings.filter(started=None).exists()
    ):
        raise Http404()

    new_task = task.reopen(user=request.user)
    return redirect(new_task.url)

@task_required
@with_task_management
def categorization_review(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    return readonly_submission_form(request,
        submission_form=submission.current_submission_form,
        extra_context={
            'categorization_review': True,
            'categorization_task': request.related_tasks[0].review_for,
        })


@task_required
@with_task_management
def initial_review(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    return readonly_submission_form(request, submission_form=submission.current_submission_form)


@user_flag_required('is_internal')
@with_task_management
def paper_submission_review(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    task = submission.paper_submission_review_task
    if not task.assigned_to == request.user:
        task.accept(request.user)
        return redirect('ecs.core.views.submissions.paper_submission_review', submission_pk=submission_pk)
    return readonly_submission_form(request, submission_form=submission.current_submission_form)


@user_flag_required('is_internal')
def biased_board_members(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    biased_users = list(submission.biased_board_members.select_related('profile').order_by(
        'last_name', 'first_name', 'email'))

    with sudo():
        tasks = groupby(
            Task.objects.for_submission(submission)
                .filter(assigned_to__in=biased_users)
                .exclude(workflow_token__node__uid__in=('resubmission', 'b2_resubmission'))
                .open()
                .order_by('assigned_to_id', 'task_type__name'),
            lambda t: t.assigned_to_id
        )
        for assigned_to_id, assigned_tasks in tasks:
            for user in biased_users:
                if user.id == assigned_to_id:
                    user.assigned_tasks = list(assigned_tasks)
                    break

    form = BiasedBoardMemberForm(request.POST or None, submission=submission,
        prefix='add_biased_board_member')

    if request.method == 'POST' and form.is_valid():
        submission.biased_board_members.add(form.cleaned_data['biased_board_member'])
        return redirect('ecs.core.views.submissions.biased_board_members',
            submission_pk=submission_pk)
    return render(request, 'submissions/biased_board_members.html', {
        'submission': submission,
        'biased_users': biased_users,
        'form': form,
    })


@user_flag_required('is_internal')
def remove_biased_board_member(request, submission_pk=None, user_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    submission.biased_board_members.remove(user_pk)
    return redirect('ecs.core.views.submissions.biased_board_members',
        submission_pk=submission_pk)


@with_task_management
def show_checklist_review(request, submission_form_pk=None, checklist_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    checklist = get_object_or_404(Checklist, pk=checklist_pk)
    if not submission_form.submission == checklist.submission:
        raise Http404()
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'active_checklist': checklist.pk})


@user_flag_required('is_internal')
def drop_checklist_review(request, submission_form_pk=None, checklist_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    checklist = get_object_or_404(Checklist, pk=checklist_pk, status__in=('new', 'review_fail'))

    checklist.status = 'dropped'
    checklist.save()
    with sudo():
        Task.objects.for_data(checklist).exclude(closed_at__isnull=False).mark_deleted()
    return redirect('readonly_submission_form', submission_form_pk=submission_form_pk)


@task_required
@with_task_management
def checklist_review(request, submission_form_pk=None, blueprint_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    if request.method == 'GET' and not submission_form.is_current:
        return redirect('ecs.core.views.submissions.checklist_review', submission_form_pk=submission_form.submission.current_submission_form.pk, blueprint_pk=blueprint_pk)
    blueprint = get_object_or_404(ChecklistBlueprint, pk=blueprint_pk)

    user = request.user if blueprint.multiple else get_user('root@system.local')
    checklist, created = Checklist.unfiltered.select_for_update().update_or_create(
        blueprint=blueprint, submission=submission_form.submission, user=user,
        defaults={'last_edited_by': request.user},
    )
    if created:
        for question in blueprint.questions.order_by('text'):
            checklist.answers.get_or_create(question=question)

        # XXX: trigger the post_save signal (for locking status)
        checklist.save()

    formset = ChecklistAnswerFormSet(request.POST or None,
        prefix='checklist{}'.format(checklist.id),
        queryset=checklist.answers.order_by('question__index'))

    extra_context = {}

    if request.method == 'POST' and formset.is_valid():
        formset.save()
        checklist.save()    # XXX: trigger post_save signal

    response = readonly_submission_form(request, submission_form=submission_form,
        checklist_overwrite={checklist: formset}, extra_context=extra_context)
    response.has_errors = not formset.is_valid()
    return response


@task_required
@with_task_management
def vote_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.submission.current_pending_vote
    if not vote:
        raise Http404("This SubmissionForm has no Vote yet.")
    vote_review_form = VoteReviewForm(request.POST or None, instance=vote)
    if request.method == 'POST' and vote_review_form.is_valid():
        vote_review_form.save()

    response = readonly_submission_form(request, submission_form=submission_form, extra_context={
        'vote_review_form': vote_review_form,
        'vote_version': vote.version_number,
    })
    response.has_errors = not vote_review_form.is_valid()
    return response

@task_required
@with_task_management
def vote_preparation(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.submission.current_pending_vote

    # TODO: prevent race condition where new version is submitted while the
    # vote preparation is done
    assert submission_form.is_current

    if submission_form.submission.is_expedited:
        blueprint_slug = 'expedited_review'
    elif submission_form.submission.is_localec:
        blueprint_slug = 'localec_review'
    else:
        blueprint_slug = 'thesis_review'

    checklists = Checklist.objects.filter(submission=submission_form.submission,
        blueprint__slug=blueprint_slug, status='completed')

    text = []
    for checklist in checklists:
        text += ['>>> {0}: {1} <<<\n\n'.format(checklist.blueprint.name, checklist.last_edited_by) + '\n\n'.join('{0}. {1}\n{2} - {3}'.format(a.question.number, a.question.text, _('Yes') if a.answer else _('No'), a.comment) for a in checklist.answers.all())]
    text = '\n\n\n'.join(text)

    initial = None
    if vote is None:
        initial = {'text': text}
    form = VotePreparationForm(request.POST or None, instance=vote, initial=initial)
    form.is_preparation = True
    
    if form.is_valid():
        vote = form.save(commit=False)
        vote.submission_form = submission_form
        vote.save()

    response = readonly_submission_form(request, submission_form=submission_form, extra_context={
        'vote_review_form': form,
        'vote_version': vote.version_number if vote else 0,
    })
    response.has_errors = not form.is_valid()
    return response


@task_required
@with_task_management
def b2_vote_preparation(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    submission = submission_form.submission
    try:
        with sudo():
            vote = submission.votes.get(is_draft=True, upgrade_for__isnull=False)
    except Vote.DoesNotExist:
        vote = submission.votes.order_by('-pk')[:1][0]
        vote = Vote.objects.create(
            submission_form=submission_form, 
            result='2', 
            is_draft=True, 
            upgrade_for=vote, 
            text=vote.text,
        )

    form = B2VotePreparationForm(request.POST or None, instance=vote)
    form.is_preparation = True

    if form.is_valid():
        vote = form.save(commit=False)
        vote.submission_form = submission_form
        vote.save()
    
    response = readonly_submission_form(request, submission_form=submission.current_submission_form, extra_context={
        'vote_review_form': form,
        'vote_version': vote.version_number if vote else 0,
    })
    response.has_errors = not form.is_valid()
    return response


@with_docstash(group='ecs.core.views.submissions.create_submission_form')
def upload_document_for_submission(request):
    return upload_document(request, 'submissions/upload_form.html')

@with_docstash(group='ecs.core.views.submissions.create_submission_form')
def delete_document_from_submission(request):
    delete_document(request, int(request.GET['document_pk']))
    return redirect('ecs.core.views.submissions.upload_document_for_submission',
        docstash_key=request.docstash.key)

@with_docstash()
def create_submission_form(request):
    if request.method == 'POST' and 'initial' in request.docstash:
        del request.docstash['initial']
        # XXX: docstash will be saved further down

    form = SubmissionFormForm(request.POST or request.docstash.POST,
        initial=request.docstash.get('initial', {}).get('submission_form'))
    formsets = get_submission_formsets(request.POST or request.docstash.POST,
        initial=request.docstash.get('initial'))

    documents = Document.objects.filter(pk__in=request.docstash.get('document_pks', []))
    protocol_uploaded = documents.filter(doctype__identifier='protocol').exists()

    if request.method == 'GET' and not request.docstash.POST and \
        not 'initial' in request.docstash:

        protocol_uploaded = True    # don't show error on completely new
                                    # submission

        # neither docstash nor POST data: this is a completely new submission
        # => prepopulate submitter_* fields with the presenters data
        profile = request.user.profile
        form.initial.update({
            'submitter_contact_first_name': request.user.first_name,
            'submitter_contact_last_name': request.user.last_name,
            'submitter_email': request.user.email,
            'submitter_contact_gender': profile.gender,
            'submitter_contact_title': profile.title,
            'submitter_organisation': profile.organisation,
            'submitter_jobtitle': profile.jobtitle,
        })

    if 'notification_type_id' in request.docstash:
        notification_type = NotificationType.objects.get(
            id=request.docstash['notification_type_id'])
    else:
        notification_type = None

    if 'submission_id' in request.docstash:
        submission = Submission.objects.get(
            id=request.docstash['submission_id'])
    else:
        submission = None

    valid = False

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        save = request.POST.get('save', False)
        autosave = request.POST.get('autosave', False)

        request.docstash.name = (
            request.POST.get('german_project_title') or
            request.POST.get('project_title')
        )
        request.docstash.POST = request.POST
        request.docstash.save()

        if save or autosave:
            return HttpResponse('save successfull')

        for name, formset in formsets.items():
            formset.full_clean()        # work around django bug: full_clean does not get called in is_valid if total_form_count==0

        formsets_valid = all([formset.is_valid() for formset in formsets.values()]) # non-lazy validation of formsets
        valid = form.is_valid() and formsets_valid and protocol_uploaded and not 'upload' in request.POST
        if valid and submission and not notification_type and \
            not submission.current_submission_form.allows_resubmission(request.user):

            messages.error(request,
                _("This form can't be submitted at the moment."))
            valid = False

        if submit and valid:
            if not submission:
                submission = Submission.objects.create()
            submission_form = form.save(commit=False)
            submission_form.submission = submission
            submission_form.is_notification_update = bool(notification_type)
            submission_form.is_transient = bool(notification_type)
            submission_form.save()
            form.save_m2m()

            submission_form.documents = documents
            for doc in documents:
                doc.parent_object = submission_form
                doc.save()
        
            investigators = formsets.pop('investigator').save(commit=False)
            employees = formsets.pop('investigatoremployee').save(commit=False)
            for investigator in investigators:
                investigator.submission_form = submission_form
                investigator.save()
            for employee in employees:
                if employee.investigator_index >= len(investigators):
                    continue
                employee.investigator = investigators[employee.investigator_index]
                employee.save()

            for formset in formsets.values():
                for instance in formset.save(commit=False):
                    instance.submission_form = submission_form
                    instance.save()

            request.docstash.delete()
            
            on_study_submit.send(Submission, submission=submission, form=submission_form, user=request.user)

            if notification_type:
                return redirect('ecs.notifications.views.create_diff_notification',
                    submission_form_pk=submission_form.pk,
                    notification_type_pk=notification_type.pk)

            return redirect('readonly_submission_form',
                submission_form_pk=submission_form.submission.current_submission_form.pk)

    # logging.error(submission.current_submission_form)
    # If this form is new, we assume it is the new medtech law
    if submission is None:
        is_new_mpg = True
    is_old_mpg = submission is not None and submission.current_submission_form.is_mpg and submission.current_submission_form.submission_type is None

    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'valid': valid,
        'submission': submission,
        'notification_type': notification_type,
        'protocol_uploaded': protocol_uploaded,
        'is_new_mpg': is_new_mpg
    }
    for prefix, formset in formsets.items():
        context['%s_formset' % prefix] = formset
    return render(request, 'submissions/form.html', context)


def change_submission_presenter(request, submission_pk=None):
    profile = request.user.profile
    if profile.is_executive:
        submission = get_object_or_404(Submission, pk=submission_pk)
    else:
        submission = get_object_or_404(Submission, pk=submission_pk, presenter=request.user)

    previous_presenter = submission.presenter
    form = PresenterChangeForm(request.POST or None, instance=submission)

    if request.method == 'POST' and form.is_valid():
        new_presenter = form.cleaned_data['presenter']
        submission.presenter = new_presenter
        submission.save(update_fields=('presenter',))
        on_presenter_change.send(Submission, 
            submission=submission, 
            old_presenter=previous_presenter, 
            new_presenter=new_presenter, 
            user=request.user,
        )
        if request.user == previous_presenter:
            return redirect('ecs.dashboard.views.view_dashboard')
        else:
            return redirect('view_submission', submission_pk=submission.pk)

    return render(request, 'submissions/change_presenter.html', {'form': form, 'submission': submission})


def change_submission_susar_presenter(request, submission_pk=None):
    profile = request.user.profile
    if profile.is_executive:
        submission = get_object_or_404(Submission, pk=submission_pk)
    else:
        submission = get_object_or_404(Submission, pk=submission_pk, susar_presenter=request.user)

    previous_susar_presenter = submission.susar_presenter
    form = SusarPresenterChangeForm(request.POST or None, instance=submission)

    if request.method == 'POST' and form.is_valid():
        new_susar_presenter = form.cleaned_data['susar_presenter']
        submission.susar_presenter = new_susar_presenter
        submission.save(update_fields=('susar_presenter',))
        on_susar_presenter_change.send(Submission, 
            submission=submission, 
            old_susar_presenter=previous_susar_presenter, 
            new_susar_presenter=new_susar_presenter, 
            user=request.user,
        )
        if request.user == previous_susar_presenter:
            return redirect('ecs.dashboard.views.view_dashboard')
        else:
            return redirect('view_submission', submission_pk=submission.pk)

    return render(request, 'submissions/change_susar_presenter.html', {'form': form, 'submission': submission})


@with_docstash(group='ecs.core.views.submissions.create_submission_form')
def delete_docstash_entry(request):
    request.docstash.delete()
    return redirect_to_next_url(request, reverse('ecs.dashboard.views.view_dashboard'))


def export_submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk)
    if not request.user.profile.is_internal and \
        request.user != submission.presenter:
        raise Http404()
    serializer = Serializer()
    with tempfile.TemporaryFile(mode='w+b') as tmpfile:
        serializer.write(submission.current_submission_form, tmpfile)
        tmpfile.seek(0)
        response = HttpResponse(tmpfile.read(), content_type='application/ecx')
    response['Content-Disposition'] = 'attachment;filename=%s.ecx' % submission.get_ec_number_display(separator='-')
    return response


def import_submission_form(request):
    form = SubmissionImportForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        return copy_submission_form(request, submission_form_pk=form.submission_form.pk, delete=True)
    return render(request, 'submissions/import.html', {
        'form': form,
    })


def diff(request, old_submission_form_pk, new_submission_form_pk):
    old_submission_form = get_object_or_404(SubmissionForm, pk=old_submission_form_pk)
    new_submission_form = get_object_or_404(SubmissionForm, pk=new_submission_form_pk)

    diff = diff_submission_forms(old_submission_form, new_submission_form)

    return render(request, 'submissions/diff/diff.html', {
        'submission': new_submission_form.submission,
        'diff': diff,
    })


def submission_list(request, submissions, stashed_submission_forms=None, template='submissions/list.html', keyword=None, filter_form=SubmissionFilterForm, filtername='submission_filter', extra_context=None, title=None):
    if not title:
        title = _('Submissions')
    usersettings = request.user.ecs_settings

    filterform = filter_form(request.POST or getattr(usersettings, filtername))

    submissions = (filterform.filter_submissions(submissions, request.user)
        .exclude(current_submission_form=None)
        .select_related('current_submission_form')
        .only(
            'ec_number',

            'current_submission_form__project_title',
            'current_submission_form__german_project_title',
        ).prefetch_related(
            Prefetch('meetings', queryset=
                Meeting.unfiltered.only('start', 'title').order_by('start')),
        ).distinct()
        .order_by('-ec_number'))

    if request.user.profile.is_internal:
        submissions = submissions.prefetch_related(
            'tags',
            Prefetch('medical_categories',
                queryset=MedicalCategory.objects.order_by('abbrev')),
        )

    if stashed_submission_forms:
        submissions = list(stashed_submission_forms) + list(submissions)

    paginator = Paginator(submissions, 20, allow_empty_first_page=True)
    try:
        submissions = paginator.page(int(filterform.cleaned_data['page']))
    except (EmptyPage, InvalidPage):
        submissions = paginator.page(1)
        filterform.cleaned_data['page'] = 1
        filterform = filter_form(filterform.cleaned_data)
        filterform.is_valid()

    visible_submission_pks = [s.pk for s in submissions.object_list if not isinstance(s, DocStash)]

    tasks = Task.objects.open()

    # get related objects for every submission
    submission_ct = ContentType.objects.get_for_model(Submission)
    vote_ct = ContentType.objects.get_for_model(Vote)
    resubmission_tasks = tasks.filter(content_type=submission_ct, data_id__in=visible_submission_pks,
        task_type__workflow_node__uid='resubmission')
    paper_submission_tasks = tasks.filter(content_type=submission_ct, data_id__in=visible_submission_pks,
        task_type__workflow_node__uid='paper_submission_review')
    b2_resubmission_tasks = tasks.filter(content_type=vote_ct,
        data_id__in=Vote.objects.filter(submission_form__submission__pk__in=visible_submission_pks).values('pk').query,
        task_type__workflow_node__uid='b2_resubmission')

    for s in submissions.object_list:
        if isinstance(s, DocStash):
            continue
        for task in resubmission_tasks:
            if task.data == s:
                s.resubmission_task = task
        for task in paper_submission_tasks:
            if task.data == s:
                s.paper_submission_task = task
        for task in b2_resubmission_tasks:
            if task.data.submission_form.submission == s:
                s.b2_resubmission_task = task

    # save the filter in the user settings
    if 'tags' in filterform.cleaned_data:
        filterform.cleaned_data['tags'] = \
            [t.pk for t in filterform.cleaned_data['tags']]
    setattr(usersettings, filtername, filterform.cleaned_data)
    usersettings.save()
    
    data = {
        'submissions': submissions,
        'filterform': filterform,
        'keyword': keyword,
        'title': title,
        'diff_notification_types': NotificationType.objects.filter(includes_diff=True).order_by('name'),
    }

    data.update(extra_context or {})

    return render(request, template, data)


@user_flag_required('is_internal')
def xls_export(request):
    from ecs.core.tasks import xls_export
    xls_export.apply_async(kwargs={
        'user_id': request.user.id,

        # Use same filters as selected in the HTML view.
        'filters': request.user.ecs_settings.submission_filter_all,
    })

    messages.info(request,
        _('The XLS export has been started. You will get a message when the file is ready.'))

    return redirect('ecs.core.views.submissions.all_submissions')


@user_flag_required('is_internal')
def xls_export_download(request, shasum=None):
    cache_file = os.path.join(settings.ECS_DOWNLOAD_CACHE_DIR,
        '{}.xls'.format(shasum))
    response = FileResponse(open(cache_file, 'rb'),
        content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=submission-export.xls'
    return response


def all_submissions(request):
    keyword = request.GET.get('keyword', None)

    submissions = Submission.objects.all()

    if keyword is None:
        kwargs = {
            'filtername': 'submission_filter_all',
            'filter_form': AllSubmissionsFilterForm,
            'title': _('All Studies'),
            'extra_context': {
                'allow_export': request.user.profile.is_internal,
            }
        }
        return submission_list(request, submissions, **kwargs)

    keyword = keyword.strip()

    m = re.match(r'\+(\d{1,4})(/\d{1,4})?$', keyword)
    if m:
        num = int(m.group(1))
        if m.group(2):
            year = int(m.group(2)[1:])
            q = Q(ec_number=year*10000+num)
        else:
            q = Q(ec_number__endswith='{0:04}'.format(num))

        try:
            submission = submissions.filter(q).order_by('-ec_number')[0]
        except IndexError:
            pass
        else:
            return redirect('view_submission', submission_pk=submission.pk)

    submissions_q = None
    extra_context = {'keyword': keyword}

    if re.match(r'^[a-zA-Z0-9]{32}$', keyword):
        try:
            doc = Document.objects.get(downloadhistory__uuid=keyword,
                doctype__identifier='submissionform')
        except Document.DoesNotExist:
            pass
        else:
            extra_context['matched_document'] = doc
            if doc.content_type_id == ContentType.objects.get_for_model(Submission).id:
                submissions_q = Q(pk=doc.object_id)
            elif doc.content_type_id == ContentType.objects.get_for_model(SubmissionForm).id:
                submissions_q = Q(forms__pk=doc.object_id)
            if isinstance(doc.parent_object, SubmissionForm) and not doc.parent_object.is_current:
                extra_context['warning'] = _('This document is an old version.')

    def _query(f, k, exact=False):
        return Q(**{'{0}__{1}'.format(f, 'iexact' if exact else 'icontains'): k})

    def _sf_query(f, k, exact=False):
        return _query('current_submission_form__{0}'.format(f), k, exact=exact)

    checklist_ct = ContentType.objects.get_for_model(Checklist)
    with sudo():
        external_review_tasks = Task.objects.filter(content_type=checklist_ct, task_type__workflow_node__uid='external_review')
    def _external_reviewer_query(*args, **kwargs):
        with sudo():
            user_pks = User.objects.filter(*args, **kwargs).values('pk').query
            checklist_pks = external_review_tasks.filter(assigned_to__pk__in=user_pks).values('data_id').query
            checklists = Checklist.objects.filter(pk__in=checklist_pks)
            pks = list(checklists.values_list('submission__pk', flat=True))
        return Q(pk__in=pks)

    if submissions_q is None:
        submissions_q = Q()
        for k in keyword.split():
            q = Q()

            m = re.match(r'(\d{1,4})(/\d{1,4})?$', k)
            if m:
                num = int(m.group(1))
                if m.group(2):
                    year = int(m.group(2)[1:])
                    q |= Q(ec_number=year*10000+num)
                else:
                    q |= Q(ec_number__endswith='{0:04}'.format(num))

            for f in ('project_title', 'german_project_title', 'sponsor_name', 'eudract_number'):
                q |= _sf_query(f, k)

            for f in ('presenter', 'susar_presenter'):
                q |= _query('{0}__first_name'.format(f), k)
                q |= _query('{0}__last_name'.format(f), k)

            for f in ('submitter', 'sponsor', 'investigators_'):
                q |= _sf_query('{0}_contact_first_name'.format(f), k)
                q |= _sf_query('{0}_contact_last_name'.format(f), k)

            for f in ('presenter', 'submitter', 'investigators__user', 'sponsor'):
                q |= _sf_query('{0}__first_name'.format(f), k)
                q |= _sf_query('{0}__last_name'.format(f), k)

            if request.user.profile.is_internal:
                q |= _external_reviewer_query(Q(first_name__icontains=k)|Q(last_name__icontains=k))
                q |= _query('tags__name', k)

            if '@' in keyword:
                for f in ('presenter', 'susar_presenter'):
                    q |= _query('{0}__email'.format(f), k, exact=True)

                for f in ('submitter', 'sponsor', 'investigators_'):
                    q |= _sf_query('{0}_email'.format(f), k, exact=True)

                for f in ('presenter', 'submitter', 'investigators__user', 'sponsor'):
                    q |= _sf_query('{0}__email'.format(f), k, exact=True)

                if request.user.profile.is_internal:
                    q |= _external_reviewer_query(Q(email__iexact=k))

            submissions_q &= q

    submissions = submissions.filter(submissions_q)
    kwargs = {
        'filtername': 'submission_filter_search',
        'filter_form': SubmissionMinimalFilterForm,
        'extra_context': extra_context,
        'title': _('Study Search'),
    }
    return submission_list(request, submissions, **kwargs)


def assigned_submissions(request):
    submissions = Submission.objects.reviewed_by_user(request.user)

    return submission_list(request, submissions,
        filtername='submission_filter_assigned',
        filter_form=AssignedSubmissionsFilterForm,
        title=_('Assigned Studies'),
    )


def my_submissions(request):
    submissions = Submission.unfiltered.mine(request.user)

    stashed = (DocStash.objects
        .filter(group='ecs.core.views.submissions.create_submission_form',
            owner=request.user, object_id=None, current_version__gte=0)
        .order_by('-modtime')
    )

    return submission_list(request, submissions,
        stashed_submission_forms=stashed,
        filtername='submission_filter_mine',
        filter_form=SubmissionMinimalFilterForm,
        title=_('My Studies'),
    )


@forceauth.exempt
@cache_page(60 * 60)
def catalog(request, year=None):
    with sudo():
        votes = (Vote.objects
            .filter(result='1', published_at__lte=timezone.now())
            .select_related('submission_form', 'submission_form__submission')
            .prefetch_related(
                Prefetch('submission_form__investigators',
                    Investigator.objects.system_ec(),
                    to_attr='system_ec_investigators'),
                Prefetch('submission_form__investigators',
                    Investigator.objects.non_system_ec(),
                    to_attr='non_system_ec_investigators')
            ).annotate(
                first_meeting_start=
                    Min('submission_form__submission__meetings__start')
            ).order_by('published_at')
        )

        years = votes.datetimes('published_at', 'year')
        if year is None:
            try:
                year = list(years)[-1].year
            except IndexError:  # no votes yet
                year = timezone.now().year
                years = [year]

            return redirect('ecs.core.views.submissions.catalog', year=year)
        else:
            year = int(year)
        votes = votes.filter(published_at__year=int(year))
        html = render(request, 'submissions/catalog.html', {
            'year': year,
            'years': years,
            'votes': votes,
        })
    return html


@forceauth.exempt
@cache_page(60 * 60)
def catalog_json(request):
    data = [{
        'version': '2.0',
        'copyright': '(C) under the Creative Commons License BY-SA 3.0: {0}'.format(
            EthicsCommission.objects.get(
                uuid=settings.ETHICS_COMMISSION_UUID).name),
        'copyright_url': 'http://creativecommons.org/licenses/by-sa/3.0/at/',
    }]
    
    with sudo():
        votes = (Vote.objects
            .filter(result='1', published_at__lte=timezone.now())
            .select_related('submission_form', 'submission_form__submission')
            .prefetch_related(
                Prefetch('submission_form__investigators',
                    Investigator.objects.system_ec(),
                    to_attr='system_ec_investigators'),
                Prefetch('submission_form__investigators',
                    Investigator.objects.non_system_ec(),
                    to_attr='non_system_ec_investigators')
            ).annotate(
                first_meeting_start=
                    Min('submission_form__submission__meetings__start')
            ).order_by('published_at')
        )
        for vote in votes:
            sf = vote.submission_form
            item = {
                'title_de': sf.german_project_title,
                'title_en': sf.project_title,
                'ec_number': sf.submission.get_ec_number_display(),
                'sponsor': sf.sponsor_name,
                'date_of_vote':
                    timezone.localtime(vote.published_at)
                        .strftime('%Y-%m-%d'),
                'date_of_first_meeting':
                    timezone.localtime(vote.first_meeting_start)
                        .strftime('%Y-%m-%d'),
                'other_investigators_count': len(sf.non_system_ec_investigators),
            }
            if sf.project_type_education_context:
                item.update({
                    'project_type': sf.get_project_type_education_context_display(),
                    'submitter': str(sf.submitter_contact),
                })

            item['investigators'] = [{
                'organisation': i.organisation,
                'name': str(i.contact),
            } for i in sf.system_ec_investigators]

            data.append(item)

    return JsonResponse(data, safe=False)


@user_flag_required('is_executive')
def grant_temporary_access(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    form = TemporaryAuthorizationForm(request.POST or None, prefix='temp_auth')
    if form.is_valid():
        temp_auth = form.save(commit=False)
        temp_auth.submission = submission
        temp_auth.save()
    return redirect(reverse('ecs.core.views.submissions.view_submission', kwargs={'submission_pk': submission_pk}) + '#involved_parties_tab')


@user_flag_required('is_executive')
def revoke_temporary_access(request, submission_pk=None, temp_auth_pk=None):
    temp_auth = get_object_or_404(TemporaryAuthorization, pk=temp_auth_pk)
    temp_auth.end = timezone.now()
    temp_auth.save()
    return redirect(reverse('ecs.core.views.submissions.view_submission', kwargs={'submission_pk': submission_pk}) + '#involved_parties_tab')
