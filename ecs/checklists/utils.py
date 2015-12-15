from ecs.checklists.models import ChecklistBlueprint, ChecklistAnswer
from ecs.users.utils import get_current_user

def get_checklist_answer_instance(submission, blueprint_slug, number):
    blueprint = ChecklistBlueprint.objects.get(slug=blueprint_slug)
    q = ChecklistAnswer.objects.filter(
        checklist__submission=submission, 
        question__blueprint__pk=blueprint.pk,
        question__number=str(number)
    )
    if blueprint.multiple:
        q.filter(checklist__user=get_current_user())
    return q.get()

def get_checklist_answer(submission, blueprint_slug, number):
    return get_checklist_answer_instance(submission, blueprint_slug, number).answer
