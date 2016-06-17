from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from ecs.checklists.models import Checklist, ChecklistBlueprint
from ecs.checklists.forms import (
    ChecklistTaskCreationForm, ChecklistTaskCreationStage2Form,
)
from ecs.core.models import Submission
from ecs.documents.views import handle_download
from ecs.tasks.models import Task
from ecs.users.utils import user_flag_required, sudo


def yesno(flag):
    return flag and "Ja" or "Nein"


def checklist_comments(request, checklist_pk=None, flavour='negative'):
    checklist = get_object_or_404(Checklist, pk=checklist_pk)
    answer = flavour == 'positive'
    answers = checklist.get_answers_with_comments(answer).select_related('question')
    return HttpResponse("\n\n".join("%s\n%s: %s" % (a.question.text, yesno(a.answer), a.comment) for a in answers), content_type="text/plain")


def checklist_pdf(request, checklist_pk=None):
    checklist = get_object_or_404(Checklist, pk=checklist_pk)
    return handle_download(request, checklist.pdf_document)


@user_flag_required('is_internal')
def create_task(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)

    form = ChecklistTaskCreationForm(request.GET or request.POST or None,
        prefix='checklist_task')
    if form.is_valid():
        form_stage2 = ChecklistTaskCreationStage2Form(
            submission, form.cleaned_data['task_type'], request.POST or None,
            prefix='checklist_task')
    else:
        form_stage2 = None
    created = False

    if request.method == 'POST' and form.is_valid() and form_stage2.is_valid():
        task_type = form.cleaned_data['task_type']
        assign_to = form_stage2.cleaned_data.get('assign_to')

        with sudo():
            tasks = Task.objects.for_submission(submission).open().filter(
                task_type=task_type)
            if not task_type.is_delegatable:
                tasks = tasks.filter(assigned_to=assign_to)
            task_exists = tasks.exists()

        if task_exists:
            form.add_error('task_type', _('This task does already exist'))
        else:
            if task_type.workflow_node.uid == 'external_review':
                blueprint = ChecklistBlueprint.objects.get(slug='external_review')
                checklist, created = Checklist.objects.get_or_create(
                    blueprint=blueprint, submission=submission, user=assign_to,
                    defaults={'last_edited_by': assign_to})
                if created:
                    for question in blueprint.questions.order_by('text'):
                        checklist.answers.get_or_create(question=question)
                elif checklist.status == 'dropped':
                    checklist.status = 'new'
                    checklist.save()
                    with sudo():
                        task = Task.objects.for_data(checklist).filter(
                            task_type__workflow_node__uid='external_review'
                        ).first().reopen()
                        task.created_by = request.user
                        task.accepted = False
                        task.save()

                with sudo():
                    task = Task.objects.for_data(checklist).open().filter(
                        task_type=task_type).get()

            else:
                token = task_type.workflow_node.bind(
                    submission.workflow.workflows[0]).receive_token(None)
                token.task.assign(user=assign_to)
                task = token.task

            task.created_by = request.user
            task.save()

            form = ChecklistTaskCreationForm(None, prefix='checklist_task')
            form_stage2 = None
            created = True

    return render(request, 'checklists/create_task.html', {
        'form': form,
        'form_stage2': form_stage2,
        'created': created,
    })
