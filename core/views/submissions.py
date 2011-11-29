# -*- coding: utf-8 -*-
from datetime import datetime
import tempfile
import re

from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from ecs.documents.models import Document
from ecs.documents.views import handle_download
from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.core.models import Submission, SubmissionForm, TemporaryAuthorization
from ecs.checklists.models import ChecklistBlueprint, Checklist, ChecklistAnswer

from ecs.core.forms import (SubmissionFormForm, MeasureFormSet, RoutineMeasureFormSet, NonTestedUsedDrugFormSet, 
    ForeignParticipatingCenterFormSet, InvestigatorFormSet, InvestigatorEmployeeFormSet, TemporaryAuthorizationForm,
    SubmissionImportForm, SubmissionFilterForm, SubmissionMinimalFilterForm, SubmissionWidgetFilterForm, 
    PresenterChangeForm, SusarPresenterChangeForm, AssignedSubmissionsFilterForm, MySubmissionsFilterForm, AllSubmissionsFilterForm)
from ecs.core.forms.review import CategorizationReviewForm, BefangeneReviewForm
from ecs.core.forms.layout import SUBMISSION_FORM_TABS
from ecs.votes.forms import VoteReviewForm, VotePreparationForm
from ecs.core.forms.utils import submission_form_to_dict
from ecs.checklists.forms import make_checklist_form
from ecs.checklists.utils import get_checklist_comment
from ecs.notifications.models import NotificationType

from ecs.core.workflow import ChecklistReview, RecommendationReview, ExpeditedRecommendation, BoardMemberReview

from ecs.core.signals import on_study_submit, on_presenter_change, on_susar_presenter_change
from ecs.core.serializer import Serializer
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash
from ecs.votes.models import Vote
from ecs.core.diff import diff_submission_forms
from ecs.utils import forceauth
from ecs.utils.security import readonly
from ecs.users.utils import sudo, user_flag_required
from ecs.tasks.models import Task
from ecs.tasks.utils import get_obj_tasks, task_required
from ecs.users.utils import user_flag_required, user_group_required
from ecs.audit.utils import get_version_number

from ecs.documents.views import upload_document, delete_document
from ecs.core.workflow import CategorizationReview


def get_submission_formsets(data=None, instance=None, readonly=False):
    formset_classes = [
        # (prefix, formset_class, callable SubmissionForm -> initial data)
        ('measure', MeasureFormSet, lambda sf: sf.measures.filter(category='6.1')),
        ('routinemeasure', RoutineMeasureFormSet, lambda sf: sf.measures.filter(category='6.2')),
        ('nontesteduseddrug', NonTestedUsedDrugFormSet, lambda sf: sf.nontesteduseddrug_set.all()),
        ('foreignparticipatingcenter', ForeignParticipatingCenterFormSet, lambda sf: sf.foreignparticipatingcenter_set.all()),
        ('investigator', InvestigatorFormSet, lambda sf: sf.investigators.all()),
    ]
    formsets = {}
    for name, formset_cls, initial in formset_classes:
        kwargs = {'prefix': name, 'readonly': readonly, 'initial': []}
        if readonly:
            kwargs['extra'] = 0
        if instance:
            kwargs['initial'] = [model_to_dict(obj, exclude=('id',)) for obj in initial(instance).order_by('id')]
        formsets[name] = formset_cls(data, **kwargs)

    employees = []
    if instance:
        for index, investigator in enumerate(instance.investigators.order_by('id')):
            for employee in investigator.employees.order_by('id'):
                employee_dict = model_to_dict(employee, exclude=('id', 'investigator'))
                employee_dict['investigator_index'] = index
                employees.append(employee_dict)
    kwargs = {'prefix': 'investigatoremployee', 'readonly': readonly}
    if readonly:
        kwargs['extra'] = 0
    formsets['investigatoremployee'] = InvestigatorEmployeeFormSet(data, initial=employees or [], **kwargs)
    return formsets


def copy_submission_form(request, submission_form_pk=None, notification_type_pk=None, delete=False):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk, submission__presenter=request.user)
    if notification_type_pk:
        notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    else:
        notification_type = None

    if delete:
        docstash = DocStash.objects.create(
            group='ecs.core.views.submissions.create_submission_form',
            owner=request.user,
        )
        created = True
    else:
        docstash, created = DocStash.objects.get_or_create(
            group='ecs.core.views.submissions.create_submission_form',
            owner=request.user,
            content_type=ContentType.objects.get_for_model(Submission),
            object_id=submission_form.submission.pk,
        )

    with docstash.transaction():
        docstash.update({
            'notification_type': notification_type,
        })
        if created:
            docstash.update({
                'form': SubmissionFormForm(data=None, initial=submission_form_to_dict(submission_form)),
                'formsets': get_submission_formsets(instance=submission_form),
                'submission': submission_form.submission if not delete else None,
                'document_pks': [d.pk for d in submission_form.documents.all()],
            })
            docstash.name = "%s" % submission_form.project_title
        if delete:
            submission_form.submission.delete()

    return HttpResponseRedirect(reverse('ecs.core.views.create_submission_form', kwargs={'docstash_key': docstash.key}))


@readonly()
def copy_latest_submission_form(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    submission_form = submission.newest_submission_form
    return HttpResponseRedirect(reverse('ecs.core.views.copy_submission_form', kwargs={
        'submission_form_pk': submission_form.pk
    }))


@readonly()
def view_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission.current_submission_form.pk}))

CHECKLIST_ACTIVITIES = (ChecklistReview, RecommendationReview,
    ExpeditedRecommendation, BoardMemberReview)


@readonly()
def readonly_submission_form(request, submission_form_pk=None, submission_form=None, extra_context=None, template='submissions/readonly_form.html', checklist_overwrite=None):
    if not submission_form:
        submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = SubmissionFormForm(initial=submission_form_to_dict(submission_form), readonly=True)
    formsets = get_submission_formsets(instance=submission_form, readonly=True)
    vote = submission_form.current_vote
    submission = submission_form.submission

    checklists = submission.checklists.filter(Q(status__in=('completed', 'review_ok',)) | Q(user=request.user)).order_by('blueprint__name')

    checklist_reviews = []
    for checklist in checklists:
        if checklist_overwrite and checklist in checklist_overwrite:
            checklist_form = checklist_overwrite[checklist]
        else:
            try:
                reopen_tasks = get_obj_tasks(CHECKLIST_ACTIVITIES, submission, data=checklist.blueprint)
                reopen_task = reopen_tasks.order_by('-created_at')[0]
            except IndexError:
                checklist_form = make_checklist_form(checklist)(readonly=True)
            else:
                checklist_form = make_checklist_form(checklist)(readonly=True, reopen_task=reopen_task)
        checklist_reviews.append((checklist, checklist_form))

    checklist_summary = []
    for checklist in checklists:
        if checklist.is_negative or checklist.get_all_answers_with_comments().count():
            q = Q(question__is_inverted=False, answer=False) | Q(question__is_inverted=True, answer=True)
            q |= Q(question__requires_comment=False) & ~(Q(comment=None) | Q(comment=''))
            answers = checklist.answers.filter(q)
            checklist_summary.append((checklist, answers))

    submission_forms = list(submission.forms.order_by('created_at'))
    previous_form = None
    for sf in submission_forms:
        sf.previous_form = previous_form
        previous_form = sf
    submission_forms = reversed(submission_forms)

    external_review_checklists = Checklist.objects.filter(submission=submission, blueprint__slug='external_review')
    notifications = submission.notifications.order_by('-timestamp')
    votes = submission.votes
    
    stashed_notifications = []
    for d in DocStash.objects.filter(group='ecs.notifications.views.create_notification'):
        try:
            if str(submission_form.pk) in d.current_value['form'].data['submission_forms']:
                stashed_notifications.append(d)
        except KeyError:
            pass

    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'documents': submission_form.documents.all().order_by('doctype__identifier', 'version', 'date'),
        'readonly': True,
        'submission': submission,
        'submission_form': submission_form,
        'submission_forms': submission_forms,
        'vote': vote,
        'checklist_reviews': checklist_reviews,
        'checklist_summary': checklist_summary,
        'show_reviews': any(checklist_reviews),
        'open_notifications': notifications.unanswered(),
        'answered_notifications': notifications.answered(),
        'stashed_notifications': stashed_notifications,
        'pending_votes': votes.filter(published_at__isnull=True),
        'published_votes': votes.filter(published_at__isnull=False),
        'diff_notification_types': NotificationType.objects.filter(includes_diff=True).order_by('name'),
        'external_review_checklists': external_review_checklists,
        'temporary_auth': submission.temp_auth.order_by('end'),
        'temporary_auth_form': TemporaryAuthorizationForm(),
    }

    if request.user not in (submission.presenter, submission.susar_presenter, submission_form.submitter, submission_form.sponsor):
        context['show_reviews'] = True
        context.update({
            'categorization_review_form': CategorizationReviewForm(instance=submission, readonly=True),
            'befangene_review_form': BefangeneReviewForm(instance=submission, readonly=True),
            'vote_review_form': VoteReviewForm(instance=vote, readonly=True),
        })
        if request.user.get_profile().is_executive_board_member:
            tasks = list(Task.objects.for_user(request.user, activity=CategorizationReview, data=submission).order_by('-closed_at'))
            if tasks and not [t for t in tasks if not t.closed_at]:
                context['categorization_task'] = tasks[0]

    if extra_context:
        context.update(extra_context)

    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, template, context)


@user_flag_required('is_internal')
def delete_task(request, submission_form_pk=None, task_pk=None):
    with sudo():
        task = get_object_or_404(Task, pk=task_pk)
    task.deleted_at = datetime.now()
    task.save()
    return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form_pk}))


@user_group_required('EC-Executive Board Group', 'EC-Thesis Executive Group', 'Local-EC Review Group')
def categorization_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    task = request.task_management.task

    docstash, created = DocStash.objects.get_or_create(
        group='ecs.core.views.submissions.categorization_review',
        owner=request.user,
        content_type=ContentType.objects.get_for_model(task.__class__),
        object_id=task.pk,
    )

    with docstash.transaction():
        form = docstash.get('form')
        if request.method == 'POST' or form is None:
            form = CategorizationReviewForm(request.POST or None, instance=submission_form.submission)
        docstash['form'] = form

    if request.method == 'POST' and form.is_valid():
        form.save()
        docstash.delete()

    form.bound_to_task = task

    response = readonly_submission_form(request, submission_form=submission_form, extra_context={'categorization_review_form': form,})
    if request.method == 'POST' and not form.is_valid():
        response.has_errors = True
    return response


@task_required()
def initial_review(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    return readonly_submission_form(request, submission_form=submission.current_submission_form)


@user_flag_required('is_internal', 'is_thesis_reviewer')
def paper_submission_review(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    task = submission.paper_submission_review_task_for(request.user)
    if not task.assigned_to == request.user:
        task.accept(request.user)
        return HttpResponseRedirect(reverse('ecs.core.views.paper_submission_review', kwargs={'submission_pk': submission_pk}))
    return readonly_submission_form(request, submission_form=submission.current_submission_form)


@user_flag_required('is_internal')
def befangene_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = BefangeneReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'befangene_review_form': form,})


@readonly()
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
    
    if checklist.blueprint.slug == 'external_review':
        submission_form.submission.external_reviewers.remove(checklist.user)
    
    checklist.status = 'dropped'
    checklist.save()
    with sudo():
        for task in Task.objects.for_data(checklist).exclude(closed_at__isnull=False):
            task.deleted_at = datetime.now()
            task.save()
    return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form_pk}))


@task_required()
def checklist_review(request, submission_form_pk=None, blueprint_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    blueprint = get_object_or_404(ChecklistBlueprint, pk=blueprint_pk)
    related_task = request.related_tasks[0]

    lookup_kwargs = dict(blueprint=blueprint, submission=submission_form.submission)
    if blueprint.multiple:
        lookup_kwargs['user'] = request.user
    else:
        lookup_kwargs['defaults'] = {'user': request.user}
    checklist, created = Checklist.objects.get_or_create(**lookup_kwargs)
    if created:
        for question in blueprint.questions.order_by('text'):
            answer, created = ChecklistAnswer.objects.get_or_create(checklist=checklist, question=question)
        checklist.save() # touch the checklist instance to trigger the post_save signal (for locking status)

    form = make_checklist_form(checklist)(request.POST or None, related_task=related_task)
    task = request.task_management.task
    if task:
        form.bound_to_task = task
    extra_context = {}

    if request.method == 'POST':
        complete_task = request.POST.get('complete_task') == 'complete_task'
        really_complete_task = request.POST.get('really_complete_task') == 'really_complete_task'
        if form.is_valid():
            for question in blueprint.questions.all().order_by('index'):
                answer = ChecklistAnswer.objects.get(checklist=checklist, question=question)
                answer.answer = form.cleaned_data['q%s' % question.index]
                answer.comment = form.cleaned_data['c%s' % question.index]
                answer.save()

            checklist.save() # touch the checklist instance to trigger the post_save signal

            if (complete_task or really_complete_task) and not checklist.is_complete:
                extra_context['review_incomplete'] = True
            elif really_complete_task and checklist.is_complete:
                checklist.status = 'completed'
                checklist.save()
                related_task.done(request.user)
                return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form_pk}))
            elif complete_task and checklist.is_complete:
                extra_context['review_complete'] = checklist.pk


    return readonly_submission_form(request, submission_form=submission_form, checklist_overwrite={checklist: form}, extra_context=extra_context)


@user_flag_required('is_internal')
def vote_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.current_vote
    if not vote:
        raise Http404("This SubmissionForm has no Vote yet.")
    vote_review_form = VoteReviewForm(request.POST or None, instance=vote)
    task = request.task_management.task
    if task:
        vote_review_form.bound_to_task = task
    if request.method == 'POST' and vote_review_form.is_valid():
        vote_review_form.save()

    response = readonly_submission_form(request, submission_form=submission_form, extra_context={
        'vote_review_form': vote_review_form,
        'vote_version': get_version_number(vote),
    })
    if request.method == 'POST' and not vote_review_form.is_valid():
        response.has_errors = True
    return response


@task_required()
def vote_preparation(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.current_vote
    if submission_form.submission.is_expedited:
        checklist = 'expedited_review'
    elif submission_form.submission.is_localec:
        checklist = 'localec_review'
    else:
        checklist = 'thesis_review'
    form = VotePreparationForm(request.POST or None, instance=vote, initial={
        'text': get_checklist_comment(submission_form.submission, checklist, 1)
    })
    
    form.bound_to_task = request.task_management.task
    
    if form.is_valid():
        vote = form.save(commit=False)
        vote.submission_form = submission_form
        vote.save()

    response = readonly_submission_form(request, submission_form=submission_form, extra_context={
        'vote_review_form': form,
        'vote_version': get_version_number(vote) if vote else 0,
    })
    response.has_errors = not form.is_valid()
    return response


@with_docstash_transaction(group='ecs.core.views.submissions.create_submission_form')
def upload_document_for_submission(request):
    return upload_document(request, 'submissions/upload_form.html')

@with_docstash_transaction(group='ecs.core.views.submissions.create_submission_form')
def delete_document_from_submission(request):
    delete_document(request, int(request.GET['document_pk']))
    return HttpResponseRedirect(reverse('ecs.core.views.upload_document_for_submission', kwargs={'docstash_key': request.docstash.key}))

@with_docstash_transaction
def create_submission_form(request):
    form = request.docstash.get('form')
    documents = Document.objects.filter(pk__in=request.docstash.get('document_pks', []))
    protocol_uploaded = documents.filter(doctype__identifier=u'protocol').exists()
    if request.method == 'POST' or form is None:
        form = SubmissionFormForm(request.POST or None)
        if request.method == 'GET':
            protocol_uploaded = True    # don't show error on completely new
                                        # submission

    formsets = request.docstash.get('formsets')
    if request.method == 'POST' or formsets is None:
        formsets = get_submission_formsets(request.POST or None)
        if request.method == 'GET':
            # neither docstash nor POST data: this is a completely new submission
            # => prepopulate submitter_* fields with the presenters data
            profile = request.user.get_profile()
            form.initial.update({
                'submitter_contact_first_name': request.user.first_name,
                'submitter_contact_last_name': request.user.last_name,
                'submitter_email': request.user.email,
                'submitter_contact_gender': profile.gender,
                'submitter_contact_title': profile.title,
                'submitter_organisation': profile.organisation,
                'submitter_jobtitle': profile.jobtitle,
            })

    notification_type = request.docstash.get('notification_type', None)
    valid = False

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        save = request.POST.get('save', False)
        autosave = request.POST.get('autosave', False)

        request.docstash.update({
            'form': form,
            'formsets': formsets,
        })
        
        # set docstash name
        project_title_german = request.POST.get('german_project_title', '')
        if project_title_german:
            request.docstash.name = project_title_german
        else:
            request.docstash.name = request.POST.get('project_title', '')

        if save or autosave:
            return HttpResponse('save successfull')

        formsets_valid = all([formset.is_valid() for formset in formsets.itervalues()]) # non-lazy validation of formsets
        valid = form.is_valid() and formsets_valid and protocol_uploaded and not 'upload' in request.POST

        if submit and valid and request.user.get_profile().is_approved_by_office:
            submission_form = form.save(commit=False)
            submission = request.docstash.get('submission')
            if submission:   # refetch submission object because it could have changed
                submission = Submission.objects.get(pk=submission.pk)
            else:
                submission = Submission.objects.create()
            submission_form.submission = submission
            submission_form.is_notification_update = bool(notification_type)
            submission_form.is_transient = bool(notification_type)
            submission_form.save()
            form.save_m2m()

            submission_form.documents = documents
            for doc in documents:
                doc.parent_object = submission_form
                doc.save()
        
            formsets = formsets.copy()
            investigators = formsets.pop('investigator').save(commit=False)
            for investigator in investigators:
                investigator.submission_form = submission_form
                investigator.save()
            for i, employee in enumerate(formsets.pop('investigatoremployee').save(commit=False)):
                employee.investigator = investigators[int(request.POST['investigatoremployee-%s-investigator_index' % i])]
                employee.save()

            for formset in formsets.itervalues():
                for instance in formset.save(commit=False):
                    instance.submission_form = submission_form
                    instance.save()
            request.docstash.delete()
            
            on_study_submit.send(Submission, submission=submission, form=submission_form, user=request.user)

            if notification_type:
                return HttpResponseRedirect(reverse('ecs.notifications.views.create_diff_notification', kwargs={
                    'submission_form_pk': submission_form.pk,
                    'notification_type_pk': notification_type.pk,
                }))

            return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk}))

    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'valid': valid,
        'submission': request.docstash.get('submission', None),
        'notification_type': notification_type,
        'protocol_uploaded': protocol_uploaded,
    }
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, 'submissions/form.html', context)


def change_submission_presenter(request, submission_pk=None):
    profile = request.user.get_profile()
    if profile.is_executive_board_member:
        submission = get_object_or_404(Submission, pk=submission_pk)
    else:
        submission = get_object_or_404(Submission, pk=submission_pk, presenter=request.user)

    previous_presenter = submission.presenter
    form = PresenterChangeForm(request.POST or None, instance=submission)

    if request.method == 'POST' and form.is_valid():
        new_presenter = form.cleaned_data['presenter']
        submission.presenter = new_presenter
        submission.save()
        on_presenter_change.send(Submission, 
            submission=submission, 
            old_presenter=previous_presenter, 
            new_presenter=new_presenter, 
            user=request.user,
        )
        if request.user == previous_presenter:
            return HttpResponseRedirect(reverse('ecs.dashboard.views.view_dashboard'))
        else:
            return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission.current_submission_form.pk}))

    return render(request, 'submissions/change_presenter.html', {'form': form, 'submission': submission})


def change_submission_susar_presenter(request, submission_pk=None):
    profile = request.user.get_profile()
    if profile.is_executive_board_member:
        submission = get_object_or_404(Submission, pk=submission_pk)
    else:
        submission = get_object_or_404(Submission, pk=submission_pk, susar_presenter=request.user)

    previous_susar_presenter = submission.susar_presenter
    form = SusarPresenterChangeForm(request.POST or None, instance=submission)

    if request.method == 'POST' and form.is_valid():
        new_susar_presenter = form.cleaned_data['susar_presenter']
        submission.susar_presenter = new_susar_presenter
        submission.save()
        on_susar_presenter_change.send(Submission, 
            submission=submission, 
            old_susar_presenter=previous_susar_presenter, 
            new_susar_presenter=new_susar_presenter, 
            user=request.user,
        )
        if request.user == previous_susar_presenter:
            return HttpResponseRedirect(reverse('ecs.dashboard.views.view_dashboard'))
        else:
            return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission.current_submission_form.pk}))

    return render(request, 'submissions/change_susar_presenter.html', {'form': form, 'submission': submission})


@with_docstash_transaction(group='ecs.core.views.submissions.create_submission_form')
def delete_docstash_entry(request):
    request.docstash.delete()
    return redirect_to_next_url(request, reverse('ecs.dashboard.views.view_dashboard'))


@readonly()
def submission_pdf(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    return handle_download(request, submission_form.pdf_document)


@readonly()
def export_submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk)
    if not submission.current_submission_form.allows_export(request.user):
        raise Http404()
    serializer = Serializer()
    with tempfile.TemporaryFile(mode='w+b') as tmpfile:
        serializer.write(submission.current_submission_form, tmpfile)
        tmpfile.seek(0)
        response = HttpResponse(tmpfile.read(), mimetype='application/ecx')
    response['Content-Disposition'] = 'attachment;filename=%s.ecx' % submission.get_ec_number_display(separator='-')
    return response


@user_flag_required('is_approved_by_office')
def import_submission_form(request):
    form = SubmissionImportForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        return copy_submission_form(request, submission_form_pk=form.submission_form.pk, delete=True)
    return render(request, 'submissions/import.html', {
        'form': form,
    })


@readonly()
def diff(request, old_submission_form_pk, new_submission_form_pk):
    old_submission_form = get_object_or_404(SubmissionForm, pk=old_submission_form_pk)
    new_submission_form = get_object_or_404(SubmissionForm, pk=new_submission_form_pk)

    diff = diff_submission_forms(old_submission_form, new_submission_form)

    return render(request, 'submissions/diff/diff.html', {
        'submission': new_submission_form.submission,
        'diff': diff,
    })


@readonly()
def submission_list(request, submissions, stashed_submission_forms=None, template='submissions/list.html', limit=20, keyword=None, filter_form=SubmissionFilterForm, filtername='submission_filter', order_by=None, extra_context=None, title=None):
    if not title:
        title = _('Submissions')
    usersettings = request.user.ecs_settings

    if order_by is None:
        order_by = ('ec_number',)

    filterform = filter_form(request.POST or getattr(usersettings, filtername))
    submissions = filterform.filter_submissions(submissions, request.user)
    submissions = submissions.exclude(current_submission_form__isnull=True).distinct().order_by(*order_by)
    submissions = submissions.select_related('current_submission_form')

    if stashed_submission_forms:
        submissions = [x for x in stashed_submission_forms if x.current_value] + list(submissions)

    paginator = Paginator(submissions, limit, allow_empty_first_page=True)
    try:
        submissions = paginator.page(int(filterform.cleaned_data['page']))
    except (EmptyPage, InvalidPage):
        submissions = paginator.page(1)
        filterform.cleaned_data['page'] = 1
        filterform = filter_form(filterform.cleaned_data)
        filterform.is_valid()

    visible_submission_pks = [s.pk for s in submissions.object_list if not isinstance(s, DocStash)]

    tasks = Task.objects.filter(closed_at=None, deleted_at=None)

    # get related tasks for every submission
    submission_ct = ContentType.objects.get_for_model(Submission)
    vote_ct = ContentType.objects.get_for_model(Vote)
    resubmission_tasks = tasks.filter(content_type=submission_ct, data_id__in=visible_submission_pks,
        task_type__workflow_node__uid='resubmission')
    paper_submission_tasks = tasks.filter(content_type=submission_ct, data_id__in=visible_submission_pks,
        task_type__workflow_node__uid__in=['paper_submission_review', 'thesis_paper_submission_review'])
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
                s.paper_submission_review_task = task
        for task in b2_resubmission_tasks:
            if task.data.submission_form.submission == s:
                s.b2_resubmission_task = task

    checklist_ct = ContentType.objects.get_for_model(Checklist)
    external_review_tasks = tasks.filter(content_type=checklist_ct,
        data_id__in=Checklist.objects.filter(submission__in=visible_submission_pks).values('pk').query,
        task_type__workflow_node__uid='external_review')
    for s in submissions.object_list:
        if isinstance(s, DocStash):
            continue
        for task in external_review_tasks:
            if task.data.submission == s:
                s.external_review_task = task


    # save the filter in the user settings
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


@readonly()
def submission_widget(request, template='submissions/widget.html'):
    data = dict(template='submissions/widget.html', limit=5, order_by=('-ec_number',))

    if request.user.get_profile().is_internal:
        data['submissions'] = Submission.objects.all()
        data['filtername'] = 'submission_filter_widget_internal'
        data['filter_form'] = SubmissionWidgetFilterForm
    else:
        stashed = list(DocStash.objects.filter(group='ecs.core.views.submissions.create_submission_form', owner=request.user, object_id__isnull=True))
        stashed = list(sorted([s for s in stashed if s.modtime], key=lambda s: s.modtime, reverse=True)) + [s for s in stashed if not s.modtime]

        data['submissions'] = Submission.objects.mine(request.user) | Submission.objects.reviewed_by_user(request.user)
        data['stashed_submission_forms'] = stashed
        data['filtername'] = 'submission_filter_widget'
        data['filter_form'] = SubmissionFilterForm

    return submission_list(request, **data)


@readonly()
def all_submissions(request):
    keyword = request.GET.get('keyword', None)

    submissions = Submission.objects.all()
    extra_context = {
        'matched_document': None,
    }
    title = _('All Studies')
    if keyword:
        title = _('Study Search')
        submissions_q = Q(ec_number__icontains=keyword)
        m = re.match(r'(\d+)/(\d+)', keyword)
        if m:
            num = int(m.group(1))
            year = int(m.group(2))
            submissions_q |= Q(ec_number__in=[num*10000 + year, year*10000 + num])
        if re.match(r'^[a-zA-Z0-9]{32}$', keyword):
            try:
                doc = Document.objects.get(uuid=keyword)
                extra_context['matched_document'] = doc
                submissions_q |= Q(pk=doc.object_id) | Q(forms__pk=doc.object_id)
                if isinstance(doc.parent_object, SubmissionForm) and not doc.parent_object.is_current:
                    extra_context['warning'] = _('This document is an old version.')
            except Document.DoesNotExist:
                pass

        fields = ('project_title', 'german_project_title', 'sponsor_name', 'submitter_contact_last_name', 'investigators__contact_last_name', 'eudract_number')
        for field_name in fields:
            submissions_q |= Q(**{'current_submission_form__%s__icontains' % field_name: keyword})

        submissions = submissions.filter(submissions_q)

    if keyword is None:
        filter_form = AllSubmissionsFilterForm
        filtername = 'submission_filter_all'
    else:
        filter_form = SubmissionMinimalFilterForm
        filtername = 'submission_filter_search'

    return submission_list(request, submissions, keyword=keyword, filtername=filtername, filter_form=filter_form, extra_context=extra_context, title=title)


@readonly()
def assigned_submissions(request):
    submissions = Submission.objects.reviewed_by_user(request.user)
    return submission_list(request, submissions, filtername='submission_filter_assigned', filter_form=AssignedSubmissionsFilterForm, title=_('Assigned Studies'))


@readonly()
def my_submissions(request):
    submissions = Submission.objects.mine(request.user)

    stashed = list(DocStash.objects.filter(group='ecs.core.views.submissions.create_submission_form', owner=request.user, object_id__isnull=True))
    stashed = list(sorted([s for s in stashed if s.modtime], key=lambda s: s.modtime, reverse=True)) + [s for s in stashed if not s.modtime]

    return submission_list(request, submissions, stashed_submission_forms=stashed, filtername='submission_filter_mine', filter_form=MySubmissionsFilterForm, title=_('My Studies'))


@readonly()
@forceauth.exempt
def catalog(request, year=None):
    with sudo():
        votes = Vote.objects.filter(result='1', submission_form__sponsor_agrees_to_publishing=True, published_at__isnull=False, published_at__lte=datetime.now())
        votes = votes.select_related('submission_form').order_by('published_at')
        years = votes.dates('published_at', 'year')
        if year is None:
            year = list(years)[-1].year
            return HttpResponseRedirect(reverse('ecs.core.views.submissions.catalog', kwargs={'year': year}))
        else:
            year = int(year)
        votes = votes.filter(published_at__year=int(year))
        html = render(request, 'submissions/catalog.html', {
            'year': year,
            'years': years,
            'votes': votes,
        })
    return html


@readonly()
@forceauth.exempt
def catalog_json(request):
    data = []
    with sudo():
        votes = Vote.objects.filter(result='1', submission_form__sponsor_agrees_to_publishing=True, published_at__isnull=False, published_at__lte=datetime.now())
        votes = votes.select_related('submission_form').order_by('published_at')
        for vote in votes:
            sf = vote.submission_form
            item = {
                'title_de': sf.german_project_title,
                'title_en': sf.project_title,
                'ec_number': sf.submission.get_ec_number_display(),
                'sponsor': sf.sponsor_name,
                'date_of_vote': vote.published_at.strftime('%Y-%m-%d'),
                'date_of_first_meeting': sf.submission.get_first_meeting().start.strftime('%Y-%m-%d'),
                'project_type': 'Studie',
            }
            if sf.project_type_education_context:
                item.update({
                    'project_type': sf.get_project_type_education_context_display(),
                    'submitter': unicode(sf.submitter_contact),
                })
            investigators = []
            for i in sf.investigators.all():
                investigators.append({
                    'organisation': i.organisation,
                    'name': unicode(i.contact),
                    'ethics_commission': unicode(i.ethics_commission),
                })
            item['investigators'] = investigators
            data.append(item)
            
    return HttpResponse(simplejson.dumps(data, indent=4), content_type='application/json')


@user_flag_required('is_executive_board_member')
def grant_temporary_access(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    form = TemporaryAuthorizationForm(request.POST or None)
    if form.is_valid():
        temp_auth = form.save(commit=False)
        temp_auth.submission = submission
        temp_auth.save()
    return HttpResponseRedirect(reverse('ecs.core.views.view_submission', kwargs={'submission_pk': submission_pk}) + '#involved_parties_tab')


@user_flag_required('is_executive_board_member')
def revoke_temporary_access(request, submission_pk=None, temp_auth_pk=None):
    temp_auth = get_object_or_404(TemporaryAuthorization, pk=temp_auth_pk)
    temp_auth.end = datetime.now()
    temp_auth.save()
    return HttpResponseRedirect(reverse('ecs.core.views.view_submission', kwargs={'submission_pk': submission_pk}) + '#involved_parties_tab')
