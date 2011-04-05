# -*- coding: utf-8 -*-
from datetime import datetime
import tempfile
import re

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.core.files import File
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from ecs.documents.models import Document, DocumentType
from ecs.utils.viewutils import render, redirect_to_next_url, render_pdf, pdf_response
from ecs.utils.decorators import developer
from ecs.core.models import Submission, SubmissionForm, Investigator, ChecklistBlueprint, ChecklistQuestion, Checklist, ChecklistAnswer
from ecs.meetings.models import Meeting

from ecs.core.forms import SubmissionFormForm, MeasureFormSet, RoutineMeasureFormSet, NonTestedUsedDrugFormSet, ForeignParticipatingCenterFormSet, \
    InvestigatorFormSet, InvestigatorEmployeeFormSet, SubmissionEditorForm, SubmissionImportForm, \
    SubmissionFilterForm, SubmissionWidgetFilterForm, SubmissionListFilterForm, SubmissionListFullFilterForm
from ecs.core.forms.checklist import make_checklist_form
from ecs.core.forms.review import RetrospectiveThesisReviewForm, CategorizationReviewForm, BefangeneReviewForm
from ecs.core.forms.layout import SUBMISSION_FORM_TABS
from ecs.core.forms.voting import VoteReviewForm, B2VoteReviewForm
from ecs.documents.forms import DocumentForm

from ecs.core import paper_forms
from ecs.core import signals
from ecs.core.serializer import Serializer
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash
from ecs.core.models import Vote
from ecs.core.diff import diff_submission_forms
from ecs.utils import forceauth
from ecs.users.utils import sudo, user_flag_required
from ecs.tasks.models import Task
from ecs.tasks.utils import has_task
from ecs.users.utils import user_flag_required


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
    from ecs.notifications.models import NotificationType
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk, presenter=request.user)
    if notification_type_pk:
        notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    else:
        notification_type = None
    docstash = DocStash.objects.create(group='ecs.core.views.submissions.create_submission_form', owner=request.user)
    with docstash.transaction():
        docstash.update({
            'form': SubmissionFormForm(data=None, initial=model_to_dict(submission_form)),
            'formsets': get_submission_formsets(instance=submission_form),
            'submission': submission_form.submission if not delete else None,
            'documents': list(submission_form.documents.all().order_by('pk')),
            'notification_type': notification_type,
        })
        docstash.name = "%s" % submission_form.project_title
    if delete:
        submission_form.submission.delete()
    return HttpResponseRedirect(reverse('ecs.core.views.create_submission_form', kwargs={'docstash_key': docstash.key}))


def copy_latest_submission_form(request, submission_pk=None):
    submission_form = get_object_or_404(SubmissionForm, current_for_submission__pk=submission_pk)
    return HttpResponseRedirect(reverse('ecs.core.views.copy_submission_form', kwargs={
        'submission_form_pk': submission_form.pk
    }))


def view_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission.current_submission_form.pk}))


def readonly_submission_form(request, submission_form_pk=None, submission_form=None, extra_context=None, template='submissions/readonly_form.html', checklist_overwrite=None):
    if not submission_form:
        submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = SubmissionFormForm(initial=model_to_dict(submission_form), readonly=True)
    formsets = get_submission_formsets(instance=submission_form, readonly=True)
    documents = submission_form.documents.all().order_by('pk')
    vote = submission_form.current_vote
    submission = submission_form.submission

    checklist_reviews = []
    for checklist in Checklist.objects.filter(submission=submission).select_related('blueprint'):
        if checklist_overwrite and checklist in checklist_overwrite:
            checklist_form = checklist_overwrite[checklist]
        else:
            checklist_form = make_checklist_form(checklist)(readonly=True)
        checklist_reviews.append((checklist, checklist_form))
    
    submission_forms = list(submission_form.submission.forms.order_by('created_at'))
    previous_form = None
    for sf in submission_forms:
        sf.previous_form = previous_form
        previous_form = sf

    submission_forms = reversed(submission_forms)
    
    with sudo():
        cancelable_tasks = Task.objects.for_data(submission).filter(deleted_at__isnull=True, task_type__workflow_node__uid__in=['additional_review', 'external_review'], closed_at=None)

    from ecs.notifications.models import NotificationType
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'documents': documents,
        'readonly': True,
        'submission_form': submission_form,
        'submission_forms': submission_forms,
        'vote': vote,
        'checklist_reviews': checklist_reviews,
        'show_reviews': any(checklist_reviews),
        'open_notifications': submission_form.submission.notifications.filter(answer__isnull=True),
        'answered_notifications': submission_form.submission.notifications.filter(answer__isnull=False),
        'pending_votes': submission_form.submission.votes.filter(published_at__isnull=True),
        'published_votes': submission_form.submission.votes.filter(published_at__isnull=False),
        'diff_notification_types': NotificationType.objects.filter(diff=True).order_by('name'),
        'cancelable_tasks': cancelable_tasks,
    }
    
    if request.user not in (submission_form.presenter, submission_form.submitter, submission_form.sponsor):
        context['show_reviews'] = True
        context.update({
            'retrospective_thesis_review_form': RetrospectiveThesisReviewForm(instance=submission, readonly=True),
            'categorization_review_form': CategorizationReviewForm(instance=submission, readonly=True),
            'befangene_review_form': BefangeneReviewForm(instance=submission, readonly=True),
            'vote_review_form': VoteReviewForm(instance=vote, readonly=True),
        })
        if request.user.ecs_profile.executive_board_member:
            from ecs.core.workflow import CategorizationReview
            tasks = Task.objects.for_user(request.user, activity=CategorizationReview, data=submission).filter(closed_at__isnull=False).order_by('-closed_at')[:1]
            if tasks:
                context['categorization_task'] = tasks[0]
    
    if extra_context:
        context.update(extra_context)
    
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, template, context)

@user_flag_required('internal')
def delete_task(request, submission_form_pk=None, task_pk=None):
    with sudo():
        task = get_object_or_404(Task, pk=task_pk)
    task.deleted_at = datetime.now()
    task.save()
    return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form_pk}))

@user_flag_required('internal')
def retrospective_thesis_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = RetrospectiveThesisReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
        signals.post_thesis_review.send(submission_form.submission)
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'retrospective_thesis_review_form': form,})


@user_flag_required('executive_board_member')
def categorization_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = CategorizationReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'categorization_review_form': form,})


@user_flag_required('internal')
def befangene_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = BefangeneReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'befangene_review_form': form,})


def checklist_review(request, submission_form_pk=None, blueprint_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    blueprint = get_object_or_404(ChecklistBlueprint, pk=blueprint_pk)

    from ecs.core.workflow import ChecklistReview, AdditionalChecklistReview, ExternalChecklistReview
    if not has_task(request.user, (ChecklistReview, AdditionalChecklistReview, ExternalChecklistReview), submission_form.submission, data=blueprint):
        return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form_pk}))

    lookup_kwargs = dict(blueprint=blueprint, submission=submission_form.submission)
    if blueprint.multiple:
        lookup_kwargs['user'] = request.user
    else:
        lookup_kwargs['defaults'] = {'user': request.user}
    checklist, created = Checklist.objects.get_or_create(**lookup_kwargs)
    if created:
        for question in blueprint.questions.order_by('text'):
            answer, created = ChecklistAnswer.objects.get_or_create(checklist=checklist, question=question)

    form = make_checklist_form(checklist)(request.POST or None, complete_task=(blueprint.slug in ['additional_review', 'external_review']))
    extra_context = {}

    if request.method == 'POST':
        complete_task = request.POST.get('complete_task') == 'complete_task'
        really_complete_task = request.POST.get('really_complete_task') == 'really_complete_task'
        if form.is_valid():
            for i, question in enumerate(blueprint.questions.order_by('text')):
                answer = ChecklistAnswer.objects.get(checklist=checklist, question=question)
                answer.answer = form.cleaned_data['q%s' % i]
                answer.comment = form.cleaned_data['c%s' % i]
                answer.save()

            checklist.save() # touch the checklist instance to trigger the post_save signal

            if complete_task and checklist.is_complete:
                extra_context['review_complete'] = checklist.pk
            elif (complete_task or really_complete_task) and not checklist.is_complete:
                extra_context['review_incomplete'] = True
            elif really_complete_task and checklist.is_complete:
                additional_review_task = submission_form.submission.additional_review_task_for(request.user)
                external_review_task = submission_form.submission.external_review_task_for(request.user)
                if blueprint.slug == 'additional_review' and additional_review_task:
                    additional_review_task.done(request.user)
                elif blueprint.slug == 'external_review' and external_review_task:
                    external_review_task.done(request.user)
                return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form_pk}))


    return readonly_submission_form(request, submission_form=submission_form, checklist_overwrite={checklist: form}, extra_context=extra_context)


@user_flag_required('internal')
def vote_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.current_vote
    if not vote:
        raise Http404("This SubmissionForm has no Vote yet.")
    vote_review_form = VoteReviewForm(request.POST or None, instance=vote)
    if request.method == 'POST' and vote_review_form.is_valid():
        vote_review_form.save()
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'vote_review_form': vote_review_form,})


@user_flag_required('internal')
def b2_vote_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.current_vote
    if not vote or not vote.result == '2':
        raise Http404("This SubmissionForm has no B2-Vote")
    b2_vote_review_form = B2VoteReviewForm(request.POST or None, initial={
        'text': vote.text,
    })
    if request.method == 'POST' and b2_vote_review_form.is_valid():
        v = b2_vote_review_form.save(commit=False)
        v.result = '1'
        v.text = b2_vote_review_form.cleaned_data['text']
        v.submission_form = submission_form
        v.save()
        return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form_pk}) + '#vote_review_tab')
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'b2_vote_review_form': b2_vote_review_form, 'b2_vote': vote})

@with_docstash_transaction
def create_submission_form(request):
    if request.method == 'GET' and request.docstash.value:
        form = request.docstash['form']
        formsets = request.docstash['formsets']
    else:
        form = SubmissionFormForm(request.POST or None)
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
    
    doc_post = 'document-file' in request.FILES
    document_form = DocumentForm(request.POST if doc_post else None, request.FILES if doc_post else None, 
        prefix='document'
    )
    notification_type = request.docstash.get('notification_type', None)
    valid = False
    half_baked_documents = False

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        save = request.POST.get('save', False)
        autosave = request.POST.get('autosave', False)

        request.docstash.update({
            'form': form,
            'formsets': formsets,
            'documents': list(Document.objects.filter(pk__in=map(int, request.POST.getlist('documents')))),
        })
        
        # set docstash name
        project_title_german = request.POST.get('german_project_title', '')
        if project_title_german:
            request.docstash.name = project_title_german
        else:
            request.docstash.name = request.POST.get('project_title', '')

        if save or autosave:
            return HttpResponse('save successfull')
        
        if document_form.is_valid():
            documents = set(request.docstash['documents'])
            documents.add(document_form.save())
            replaced_documents = [x.replaces_document for x in documents if x.replaces_document]
            for doc in replaced_documents:  # remove replaced documents
                if doc in documents:
                    documents.remove(doc)
            request.docstash['documents'] = list(documents)
            document_form = DocumentForm(prefix='document')

        valid = form.is_valid() and all(formset.is_valid() for formset in formsets.itervalues()) and not 'upload' in request.POST

        half_baked_documents = bool([d for d in request.docstash['documents'] if not d.status == 'ready'])
        submit_now = submit and valid and request.user.get_profile().approved_by_office and not half_baked_documents

        if submit_now:
            submission_form = form.save(commit=False)
            submission = request.docstash.get('submission')
            if submission:   # refetch submission object because it could have changed
                submission = Submission.objects.get(pk=submission.pk)
            else:
                submission = Submission.objects.create()
            submission_form.submission = submission
            submission_form.presenter = request.user
            submission_form.is_notification_update = bool(notification_type)
            submission_form.transient = bool(notification_type)
            submission_form.save()
            form.save_m2m()
            submission_form.documents = request.docstash['documents']
            submission_form.save()
            for doc in request.docstash['documents']:
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

            if notification_type:
                return HttpResponseRedirect(reverse('ecs.notifications.views.create_diff_notification', kwargs={
                    'submission_form_pk': submission_form.pk,
                    'notification_type_pk': notification_type.pk,
                }))

            resubmission_task = submission.resubmission_task_for(request.user)
            if resubmission_task:
                resubmission_task.done(request.user)

            return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
    
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'document_form': document_form,
        'documents': request.docstash.get('documents', []),
        'valid': valid,
        'submission': request.docstash.get('submission', None),
        'notification_type': notification_type,
        'half_baked_documents': half_baked_documents,
    }
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, 'submissions/form.html', context)

@with_docstash_transaction(group='ecs.core.views.submissions.create_submission_form')
def delete_docstash_entry(request):
    request.docstash.delete()
    return redirect_to_next_url(request, reverse('ecs.dashboard.views.view_dashboard'))

def submission_pdf(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)    
    filename = 'ek-%s-Einreichung.pdf' % submission_form.submission.get_ec_number_display(separator='-')
    
    if not submission_form.pdf_document or not submission_form.pdf_document.status == 'new':
        pdf = render_pdf(request, 'db/submissions/xhtml2pdf/view.html', {
            'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
            'submission_form': submission_form,
            'documents': submission_form.documents.exclude(status='deleted').order_by('doctype__name', '-date'),
        })
        if not submission_form.pdf_document:
            doctype = DocumentType.objects.get(identifier='other')
            doc = Document.objects.create_from_buffer(pdf, doctype=doctype, parent_object=submission_form)
            submission_form.pdf_document = doc
            submission_form.save()
    else:
        f = submission_form.pdf_document.get_from_mediaserver()
        pdf = f.read()
        f.close()
    
    return pdf_response(pdf, filename=filename)

def export_submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk)
    submission_form = submission.current_submission_form
    serializer = Serializer()
    with tempfile.TemporaryFile(mode='w+b') as tmpfile:
        serializer.write(submission_form, tmpfile)
        tmpfile.seek(0)
        response = HttpResponse(tmpfile.read(), mimetype='application/ecx')
    response['Content-Disposition'] = 'attachment;filename=%s.ecx' % submission.get_ec_number_display(separator='-')
    return response


@user_flag_required('approved_by_office')
def import_submission_form(request):
    form = SubmissionImportForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        return copy_submission_form(request, submission_form_pk=form.submission_form.pk, delete=True)
    return render(request, 'submissions/import.html', {
        'form': form,
    })

    """
    if 'file' in request.FILES:
        serializer = Serializer()
        submission_form = serializer.read(request.FILES['file'])
        return copy_submission_form(request, submission_form_pk=submission_form.pk, delete=True)
    return render(request, 'submissions/import.html', {})
    """


def diff(request, old_submission_form_pk, new_submission_form_pk):
    old_submission_form = get_object_or_404(SubmissionForm, pk=old_submission_form_pk)
    new_submission_form = get_object_or_404(SubmissionForm, pk=new_submission_form_pk)

    diff = diff_submission_forms(old_submission_form, new_submission_form)

    return render(request, 'submissions/diff/diff.html', {
        'submission': new_submission_form.submission,
        'diff': diff,
    })

@with_docstash_transaction
def wizard(request):
    from ecs.core.forms.wizard import get_wizard_form
    if request.method == 'GET' and request.docstash.value:
        form = request.docstash['form']
        screen_form = get_wizard_form('start')(prefix='wizard')
    else:
        form = SubmissionFormForm(request.POST or None)
        name = request.POST.get('wizard-name', 'start')
        screen_form = get_wizard_form(name)(request.POST or None, prefix='wizard')
        if screen_form.is_valid():
            if screen_form.is_terminal():
                request.docstash.group = 'ecs.core.views.submissions.create_submission_form'
                request.docstash.save()
                return HttpResponseRedirect(reverse('ecs.core.views.create_submission_form', kwargs={'docstash_key': request.docstash.key}))

            typ, obj = screen_form.get_next()
            if typ == 'wizard':
                screen_form = obj(prefix='wizard')
            elif typ == 'redirect':
                return HttpResponseRedirect(obj)
            else:
                raise ValueError

    return render(request, 'submissions/wizard.html', {
        'form': screen_form,
    })

def submission_list(request, submissions, stashed_submission_forms=None, template='submissions/list.html', limit=20, keyword=None, filter_form=SubmissionFilterForm, filtername='submission_filter'):
    usersettings = request.user.ecs_settings

    filterform = filter_form(request.POST or getattr(usersettings, filtername))
    submissions = filterform.filter_submissions(submissions, request.user)
    submissions = submissions.exclude(current_submission_form__isnull=True).distinct().order_by('ec_number')

    if stashed_submission_forms:
        submissions = [x for x in stashed_submission_forms if x.current_value] + list(submissions)

    paginator = Paginator(submissions, limit, allow_empty_first_page=True)
    try:
        submissions = paginator.page(int(filterform.cleaned_data['page']))
    except EmptyPage, InvalidPage:
        submissions = paginator.page(1)
        filterform.cleaned_data['page'] = 1
        filterform = filter_form(filterform.cleaned_data)
        filterform.is_valid()

    # save the filter in the user settings
    setattr(usersettings, filtername, filterform.cleaned_data)
    usersettings.save()
    
    return render(request, template, {
        'submissions': submissions,
        'filterform': filterform,
        'keyword': keyword,
    })


def submission_widget(request, template='submissions/widget.html'):
    data = dict(template='submissions/widget.html', limit=5)

    if request.user.ecs_profile.internal:
        data['submissions'] = Submission.objects.all()
        data['filtername'] = 'submission_filter_widget_internal'
        data['filter_form'] = SubmissionWidgetFilterForm
    else:
        data['submissions'] = Submission.objects.mine(request.user) | Submission.objects.reviewed_by_user(request.user)
        data['stashed_submission_forms'] = DocStash.objects.filter(group='ecs.core.views.submissions.create_submission_form', owner=request.user)
        data['filtername'] = 'submission_filter_widget'
        data['filter_form'] = SubmissionFilterForm

    return submission_list(request, **data)

def all_submissions(request):
    keyword = request.GET.get('keyword', None)

    submissions = Submission.objects.all()
    if keyword:
        submissions_q = Q(ec_number__icontains=keyword) | Q(keywords__icontains=keyword)
        m = re.match(r'(\d+)/(\d+)', keyword)
        if m:
            num = int(m.group(1))
            year = int(m.group(2))
            submissions_q |= Q(ec_number__in=[num*10000 + year, year*10000 + num])
        if re.match(r'([a-zA-Z0-9]{5,32})', keyword):
            ct = ContentType.objects.get_for_model(Submission)
            document_q = Document.objects.filter(uuid_document__icontains=keyword, content_type=ct).values('object_id').query
            submissions_q |= Q(pk__in=document_q)
            ct = ContentType.objects.get_for_model(SubmissionForm)
            document_q = Document.objects.filter(uuid_document__icontains=keyword, content_type=ct).values('object_id').query
            submissions_q |= Q(current_submission_form__pk__in=document_q)

        fields = ('project_title', 'german_project_title', 'sponsor_name', 'submitter_contact_last_name', 'investigators__contact_last_name', 'eudract_number')
        for field_name in fields:
            submissions_q |= Q(**{'current_submission_form__%s__icontains' % field_name: keyword})

        submissions = submissions.filter(submissions_q)

    return submission_list(request, submissions, keyword=keyword, filtername='submission_filter_all', filter_form=SubmissionListFullFilterForm)

def assigned_submissions(request):
    submissions = Submission.objects.reviewed_by_user(request.user)
    return submission_list(request, submissions, filtername='submission_filter_assigned', filter_form=SubmissionListFilterForm)

def my_submissions(request):
    submissions = Submission.objects.mine(request.user)
    stashed = DocStash.objects.filter(group='ecs.core.views.submissions.create_submission_form', owner=request.user)
    return submission_list(request, submissions, stashed_submission_forms=stashed, filtername='submission_filter_mine', filter_form=SubmissionListFilterForm)

@forceauth.exempt
def catalog(request):
    with sudo():
        votes = Vote.objects.filter(result__in=('1', '1a'), submission_form__sponsor_agrees_to_publishing=True, published_at__isnull=False, published_at__lte=datetime.now()).order_by('-top__meeting__start', '-published_at')

    return render(request, 'submissions/catalog.html', {
        'votes': votes,
    })

