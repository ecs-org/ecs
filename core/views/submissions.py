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

from ecs.documents.models import Document
from ecs.utils.viewutils import render, redirect_to_next_url, render_pdf, pdf_response
from ecs.utils.decorators import developer
from ecs.core.models import Submission, SubmissionForm, Investigator, ChecklistBlueprint, ChecklistQuestion, Checklist, ChecklistAnswer
from ecs.meetings.models import Meeting

from ecs.core.forms import SubmissionFormForm, MeasureFormSet, RoutineMeasureFormSet, NonTestedUsedDrugFormSet, ForeignParticipatingCenterFormSet, \
    InvestigatorFormSet, InvestigatorEmployeeFormSet, SubmissionEditorForm, SubmissionListFilterForm
from ecs.core.forms.checklist import make_checklist_form
from ecs.core.forms.review import RetrospectiveThesisReviewForm, CategorizationReviewForm, BefangeneReviewForm
from ecs.core.forms.layout import SUBMISSION_FORM_TABS
from ecs.core.forms.voting import VoteReviewForm, B2VoteReviewForm
from ecs.documents.forms import DocumentForm, SimpleDocumentForm

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

    retrospective_thesis_review_form = RetrospectiveThesisReviewForm(instance=submission, readonly=True)
    categorization_review_form = CategorizationReviewForm(instance=submission, readonly=True)
    befangene_review_form = BefangeneReviewForm(instance=submission, readonly=True)
    vote_review_form = VoteReviewForm(instance=vote, readonly=True)
    
    checklist_reviews = []
    for checklist in submission.checklists.select_related('blueprint'):
        if checklist_overwrite and checklist in checklist_overwrite:
            checklist_form = checklist_overwrite[checklist]
        else:
            checklist_form = make_checklist_form(checklist)(readonly=True)
        checklist_reviews.append((checklist, checklist_form))
    
    submission_forms = list(submission_form.submission.forms.order_by('-created_at'))
    previous_form = None
    for sf in submission_forms:
        sf.previous_form = previous_form
        previous_form = sf
    
    from ecs.notifications.models import NotificationType
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'documents': documents,
        'readonly': True,
        'submission_form': submission_form,
        'submission_forms': submission_forms,
        'vote': vote,
        'retrospective_thesis_review_form': retrospective_thesis_review_form,
        'categorization_review_form': categorization_review_form,
        'vote_review_form': vote_review_form,
        'checklist_reviews': checklist_reviews,
        'befangene_review_form': befangene_review_form,
        'open_notifications': submission_form.submission.notifications.filter(answer__isnull=True),
        'answered_notficiations': submission_form.submission.notifications.filter(answer__isnull=False),
        'pending_votes': submission_form.submission.votes.filter(published_at__isnull=True),
        'published_votes': submission_form.submission.votes.filter(published_at__isnull=False),
        'diff_notification_types': NotificationType.objects.filter(diff=True).order_by('name'),
    }
    if extra_context:
        context.update(extra_context)
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, template, context)


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


@user_flag_required('internal')
def checklist_review(request, submission_form_pk=None, blueprint_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    blueprint = get_object_or_404(ChecklistBlueprint, pk=blueprint_pk)
    lookup_kwargs = dict(blueprint=blueprint, submission=submission_form.submission)
    if blueprint.multiple:
        lookup_kwargs['user'] = request.user
    else:
        lookup_kwargs['defaults'] = {'user': request.user}
    checklist, created = Checklist.objects.get_or_create(**lookup_kwargs)
    if created:
        for question in blueprint.questions.order_by('text'):
            answer, created = ChecklistAnswer.objects.get_or_create(checklist=checklist, question=question)
    if request.method == 'POST':
        checklist.documents = Document.objects.filter(pk__in=request.POST.getlist('documents'))
    checklist_documents = checklist.documents.all()

    form = make_checklist_form(checklist)(request.POST or None)
    
    document_form_is_empty = True
    if blueprint.min_document_count is None:
        document_form = None
    elif 'document-file' in request.FILES:
        document_form = SimpleDocumentForm(request.POST or None, request.FILES or None, prefix='document')
        if document_form.is_valid():
            doc = document_form.save()
            checklist.documents.add(doc)
            document_form = SimpleDocumentForm(prefix='document')
        else:
            document_form_is_empty = False
    else:
        document_form = SimpleDocumentForm(prefix='document')
        
    if request.method == 'POST':
        if form.is_valid() and (not document_form or document_form_is_empty or document_form.is_valid()):
            for i, question in enumerate(blueprint.questions.order_by('text')):
                answer = ChecklistAnswer.objects.get(checklist=checklist, question=question)
                answer.answer = form.cleaned_data['q%s' % i]
                answer.comment = form.cleaned_data['c%s' % i]
                answer.save()

        checklist.save() # touch the checklist instance to trigger the post_save signal

    return readonly_submission_form(request, submission_form=submission_form, checklist_overwrite={checklist: form}, extra_context={
        'checklist_document_form': document_form,
        'checklist_documents': checklist_documents,
    })


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
            # => prepopulate submitter_* fields
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

        if submit and valid and request.user.get_profile().approved_by_office:
            submission_form = form.save(commit=False)
            submission = request.docstash.get('submission') or Submission.objects.create()
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
            return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
    
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'document_form': document_form,
        'documents': request.docstash.get('documents', []),
        'valid': valid,
        'submission': request.docstash.get('submission', None),
        'notification_type': notification_type,
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
    
    if not submission_form.pdf_document:
        pdf = render_pdf(request, 'db/submissions/xhtml2pdf/view.html', {
            'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
            'submission_form': submission_form,
            'documents': submission_form.documents.filter(deleted=False).order_by('doctype__name', '-date'),
        })
        doc = Document.objects.create_from_buffer(pdf)
        submission_form.pdf_document = doc
        submission_form.save()
        pdf = doc.file.read()
    
    submission_form.pdf_document.file.seek(0)
    pdf = submission_form.pdf_document.file.read()
    return pdf_response(pdf, filename=filename)

def submission_form_list(request, submissions, stashed_submission_forms, meetings, keyword=None):
    return render(request, 'submissions/list.html', {
        'unscheduled_submissions': submissions.filter(meetings__isnull=True).distinct().order_by('ec_number'),
        'meetings': meetings,
        'stashed_submission_forms': [x for x in stashed_submission_forms if x.current_value],
        'keyword': keyword,
    })

def submission_forms(request):
    keyword = request.GET.get('keyword', None)

    if keyword:
        submissions_q = Q(ec_number__icontains=keyword) | Q(keywords__icontains=keyword)
        m = re.match(r'(\d+)/(\d+)', keyword)
        if m:
            num = int(m.group(1))
            year = int(m.group(2))
            submissions_q |= Q(ec_number__in=[num*10000 + year, year*10000 + num])
        fields = ('project_title', 'german_project_title', 'sponsor_name', 'submitter_contact_last_name', 'investigators__contact_last_name', 'eudract_number')
        for field_name in fields:
            submissions_q |= Q(**{'current_submission_form__%s__icontains' % field_name: keyword})

        submissions = Submission.objects.filter(submissions_q)
        stashed_submission_forms = DocStash.objects.none()  # XXX: we can not search in the docstash (FMD2)
        meetings = [(meeting, submissions.filter(meetings=meeting).distinct().order_by('ec_number')) for meeting in Meeting.objects.filter(submissions__pk__in=submissions.values('pk').query).order_by('-start').distinct()]
    else:
        submissions = Submission.objects.all()
        stashed_submission_forms = DocStash.objects.filter(group='ecs.core.views.submissions.create_submission_form')
        meetings = [(meeting, meeting.submissions.order_by('ec_number').distinct()) for meeting in Meeting.objects.order_by('-start')]

    return submission_form_list(request, submissions, stashed_submission_forms, meetings, keyword=keyword)

def my_submission_forms(request):
    submissions = Submission.objects.mine(request.user)
    stashed_submission_forms = DocStash.objects.filter(group='ecs.core.views.submissions.create_submission_form', owner=request.user)
    meetings = [(meeting, meeting.submissions.mine(request.user).distinct()) for meeting in Meeting.objects.filter(submissions__pk__in=submissions).distinct().order_by('-start')]

    return submission_form_list(request, submissions, stashed_submission_forms, meetings)

def assigned_submission_forms(request):
    submissions = Submission.objects.reviewed_by_user(request.user)
    stashed_submission_forms = DocStash.objects.none()
    meetings = [(meeting, meeting.submissions.filter(pk__in=submissions).distinct()) for meeting in Meeting.objects.filter(submissions__pk__in=submissions).distinct().order_by('-start')]

    return submission_form_list(request, submissions, stashed_submission_forms, meetings)

@developer
def start_workflow(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    from ecs.workflow.models import Graph
    wf = Graph.objects.get(model=Submission, auto_start=True).create_workflow(data=submission)
    wf.start()
    return HttpResponseRedirect(reverse('ecs.core.views.submission_forms'))

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

def import_submission_form(request):
    if 'file' in request.FILES:
        serializer = Serializer()
        submission_form = serializer.read(request.FILES['file'])
        return copy_submission_form(request, submission_form_pk=submission_form.pk, delete=True)
    return render(request, 'submissions/import.html', {})

def diff(request, old_submission_form_pk, new_submission_form_pk):
    old_submission_form = get_object_or_404(SubmissionForm, pk=old_submission_form_pk)
    new_submission_form = get_object_or_404(SubmissionForm, pk=new_submission_form_pk)

    diffs = diff_submission_forms(old_submission_form, new_submission_form)

    return render(request, 'submissions/diff/diff.html', {
        'submission': new_submission_form.submission,
        'diffs': diffs,
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

@user_flag_required('internal')
def submission_list(request, template='submissions/internal_list.html', limit=20):
    usersettings = request.user.ecs_settings

    filter_defaults = {
        'page': '1',
    }
    for key in ('amg', 'mpg', 'thesis', 'other', 'new', 'next_meeting', 'b2'):
        filter_defaults[key] = 'on'

    filterdict = request.POST or usersettings.submission_filter or filter_defaults
    filterform = SubmissionListFilterForm(filterdict)
    filterform.is_valid()  # force clean

    queries = {
        'new': Q(pk__in=Submission.objects.new().values('pk').query),
        'next_meeting': Q(pk__in=Submission.objects.next_meeting().values('pk').query),
        'b2': Q(pk__in=Submission.objects.b2().values('pk').query),
    }
    submissions_stage1 = Submission.objects.none()
    for key, query in queries.items():
        if filterform.cleaned_data[key]:
            submissions_stage1 |= Submission.objects.filter(query)


    queries = {
        'amg': Q(pk__in=Submission.objects.amg().values('pk').query),
        'mpg': Q(pk__in=Submission.objects.mpg().values('pk').query),
        'thesis': Q(pk__in=Submission.objects.thesis().values('pk').query),
    }
    submissions_stage2 = submissions_stage1.none()
    queries['other'] = Q(~queries['amg'] & ~queries['mpg'] & ~queries['thesis'])

    for key, query in queries.items():
        if filterform.cleaned_data[key]:
            submissions_stage2 |= submissions_stage1.filter(query)

    submissions = submissions_stage2.order_by('-current_submission_form__pk')
    paginator = Paginator(submissions, limit, allow_empty_first_page=True)
    try:
        submissions = paginator.page(int(filterform.cleaned_data['page']))
    except EmptyPage, InvalidPage:
        submissions = paginator.page(1)
        filterform.cleaned_data['page'] = 1
        filterform = SubmissionListFilterForm(filterform.cleaned_data)
        filterform.is_valid()

    # save the filter in the user settings
    usersettings.submission_filter = filterform.cleaned_data
    usersettings.save()
    
    return render(request, template, {
        'submissions': submissions,
        'filterform': filterform,
    })

@user_flag_required('internal')
def submission_widget(request, template='submissions/widget.html'):
    return submission_list(request, template=template, limit=5)

@forceauth.exempt
def catalog(request):
    with sudo():
        votes = Vote.objects.filter(result__in=('1', '1a'), submission_form__sponsor_agrees_to_publishing=True, published_at__isnull=False, published_at__lte=datetime.now()).order_by('-top__meeting__start', '-published_at')

    return render(request, 'submissions/catalog.html', {
        'votes': votes,
    })

