from ecs.checklists.models import ChecklistAnswer

def get_checklist_answer_instance(submission, blueprint_slug, number):
    return ChecklistAnswer.objects.get(
        checklist__submission=submission, 
        question__blueprint__slug=blueprint_slug, 
        question__number=str(number)
    )

def get_checklist_answer(submission, blueprint_slug, number):
    return get_checklist_answer_instance(submission, blueprint_slug, number).answer
    

def get_checklist_comment(submission, blueprint_slug, number):
    return get_checklist_answer_instance(submission, blueprint_slug, number).comment