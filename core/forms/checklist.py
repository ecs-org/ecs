from django import forms
from ecs.core.models import ChecklistBlueprint, Checklist, ChecklistAnswer, ChecklistQuestion


def make_checklist_form(checklist):
    fields = { }
    blueprint = checklist.blueprint
    for question in blueprint.questions.all():
        fields['question%s' % question.pk] = forms.NullBooleanField(label=question.text, required=False)
    form_class = type('Checklist%sForm' % blueprint.pk, (forms.BaseForm,), {'base_fields': fields})
    return form_class
