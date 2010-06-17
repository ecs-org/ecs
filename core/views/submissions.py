# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from ecs.core.views.utils import render, redirect_to_next_url
from ecs.core.models import Document, Submission, SubmissionForm, Investigator, ChecklistBlueprint, ChecklistQuestion, Checklist, ChecklistAnswer, Meeting
from ecs.core.forms import DocumentFormSet, SubmissionFormForm, MeasureFormSet, RoutineMeasureFormSet, NonTestedUsedDrugFormSet, ForeignParticipatingCenterFormSet, \
    InvestigatorFormSet, InvestigatorEmployeeFormSet, SubmissionEditorForm
from ecs.core.forms.checklist import make_checklist_form
from ecs.core.forms.review import RetrospectiveThesisReviewForm, ExecutiveReviewForm
from ecs.core.forms.layout import SUBMISSION_FORM_TABS
from ecs.core.forms.voting import VoteReviewForm
from ecs.core import paper_forms
from ecs.core import signals
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash
from ecs.utils.xhtml2pdf import xhtml2pdf


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
            for employee in investigator.investigatoremployee_set.order_by('id'):
                employee_dict = model_to_dict(employee, exclude=('id', 'investigator'))
                employee_dict['investigator_index'] = index
                employees.append(employee_dict)
    kwargs = {'prefix': 'investigatoremployee', 'readonly': readonly}
    if readonly:
        kwargs['extra'] = 0
    formsets['investigatoremployee'] = InvestigatorEmployeeFormSet(data, initial=employees or [], **kwargs)
    return formsets


def copy_submission_form(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    
    docstash = DocStash.objects.create(group='ecs.core.views.submissions.create_submission_form', owner=request.user)
    with docstash.transaction():
        docstash.update({
            'form': SubmissionFormForm(data=None, initial=model_to_dict(submission_form)),
            'formsets': get_submission_formsets(instance=submission_form),
            'submission': submission_form.submission,
            'documents': list(submission_form.documents.all().order_by('pk')),
        })
        docstash.name = "%s" % submission_form.project_title
    return HttpResponseRedirect(reverse('ecs.core.views.create_submission_form', kwargs={'docstash_key': docstash.key}))
    

def copy_latest_submission_form(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    submission_form = submission.get_most_recent_form()
    return HttpResponseRedirect(reverse('ecs.core.views.copy_submission_form', kwargs={'submission_form_pk': submission_form.pk}))


def readonly_submission_form(request, submission_form_pk=None, submission_form=None, extra_context=None, template='submissions/readonly_form.html'):
    if not submission_form:
        submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = SubmissionFormForm(initial=model_to_dict(submission_form), readonly=True)
    formsets = get_submission_formsets(instance=submission_form, readonly=True)
    documents = submission_form.documents.all().order_by('pk')
    
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'documents': documents,
        'readonly': True,
        'submission_form': submission_form,
    }
    if extra_context:
        context.update(extra_context)
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, template, context)


def retrospective_thesis_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = RetrospectiveThesisReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
        signals.post_thesis_review.send(submission_form.submission)
    return readonly_submission_form(request, submission_form=submission_form, template='submissions/reviews/retrospective_thesis.html', extra_context={
        'retrospective_thesis_review_form': form,
    })


def executive_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = ExecutiveReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return readonly_submission_form(request, submission_form=submission_form, template='submissions/reviews/executive.html', extra_context={
        'executive_review_form': form,
    })


def checklist_review(request, submission_form_pk=None, blueprint_pk=1):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    blueprint = get_object_or_404(ChecklistBlueprint, pk=blueprint_pk)
    checklist, created = Checklist.objects.get_or_create(blueprint=blueprint, submission=submission_form.submission, user=request.user)
    if created:
        for question in blueprint.questions.order_by('text'):
            answer, created = ChecklistAnswer.objects.get_or_create(checklist=checklist, question=question)
    form_class = make_checklist_form(checklist)
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        i = 0
        for question in blueprint.questions.order_by('text'):
            i = i + 1
            answer = ChecklistAnswer.objects.get(checklist=checklist, question=question)
            answer.answer = form.cleaned_data['q%s' % i]
            answer.comment = form.cleaned_data['c%s' % i]
            answer.save()
    hidden = { }
    i = 0
    for question in blueprint.questions.order_by('text'):
        i = i + 1
        answer = ChecklistAnswer.objects.get(checklist=checklist, question=question)
        hidden['q%s' % i] = False
        hidden['c%s' % i] = answer.answer is not False
    return readonly_submission_form(request, submission_form=submission_form, template='submissions/reviews/checklist.html', extra_context={
        'checklist_name': blueprint.name,
        'checklist_review_form': form,
        'checklist_hidden': hidden,
    })

def vote_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.submission.get_most_recent_vote()
    if not vote:
        raise Http404("This SubmissionForm has no Vote yet.")
    vote_form = VoteReviewForm(request.POST or None, instance=vote)
    if request.method == 'POST' and vote_form.is_valid():
        vote_form.save()
    return readonly_submission_form(request, submission_form=submission_form, template='submissions/reviews/vote.html', extra_context={
        'vote': vote,
        'vote_form': vote_form,
    })


@with_docstash_transaction
def create_submission_form(request):
    if request.method == 'GET' and request.docstash.value:
        form = request.docstash['form']
        formsets = request.docstash['formsets']
    else:
        form = SubmissionFormForm(request.POST or None)
        formsets = get_submission_formsets(request.POST or None)

    document_formset = DocumentFormSet(request.POST or None, request.FILES or None, prefix='document')

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        autosave = request.POST.get('autosave', False)

        request.docstash.update({
            'form': form,
            'formsets': formsets,
            'documents': list(Document.objects.filter(pk__in=map(int, request.POST.getlist('documents')))),
        })
        request.docstash.name = "%s" % request.POST.get('project_title', '')

        if autosave:
            return HttpResponse('autosave successfull')
        
        if document_formset.is_valid():
            request.docstash['documents'] = request.docstash['documents'] + document_formset.save()
            document_formset = DocumentFormSet(prefix='document')

        if submit and form.is_valid() and all(formset.is_valid() for formset in formsets.itervalues()):
            submission_form = form.save(commit=False)
            submission = request.docstash.get('submission') or Submission.objects.create()
            submission_form.submission = submission
            submission_form.save()
            form.save_m2m()
            submission_form.documents = request.docstash['documents']
            
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
            return HttpResponseRedirect(reverse('ecs.core.views.view_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
    
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'document_formset': document_formset,
        'documents': request.docstash.get('documents', []),
    }
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, 'submissions/form.html', context)


def view_submission_form(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    return render(request, 'submissions/view.html', {
        'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
        'submission_form': submission_form,
        'documents': submission_form.documents.filter(deleted=False).order_by('doctype__name', '-date'),
    })


def submission_pdf(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    html = render(request, 'submissions/xhtml2pdf/view.html', {
            'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
            'submission_form': submission_form,
            'documents': submission_form.documents.filter(deleted=False).order_by('doctype__name', '-date'),
            }).content
    pdf = xhtml2pdf(html)
    assert len(pdf) > 0
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=submission_%s.pdf' % submission_form_pk
    return response


def submission_form_list(request):
    submissions = Submission.objects.order_by('ec_number')
    meetings = [(meeting, meeting.submissions.order_by('ec_number')) for meeting in Meeting.objects.order_by('-start')]
    return render(request, 'submissions/list.html', {
        'unscheduled_submissions': submissions.filter(meetings__isnull=True),
        'meetings': meetings,
        'stashed_submission_forms': DocStash.objects.filter(group='ecs.core.views.submissions.create_submission_form', deleted=False),
    })


def edit_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    
    form = SubmissionEditorForm(request.POST or None, instance=submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('ecs.core.views.submission_form_list'))
    
    return render(request, 'submissions/editor.html', {
        'form': form,
        'submission': submission,
    })

# FIXME: HACK
def start_workflow(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    from ecs.workflow.models import Graph
    wf = Graph.objects.get().create_workflow(data=submission)
    wf.start()
    return HttpResponseRedirect(reverse('ecs.core.views.submission_form_list'))
