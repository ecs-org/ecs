from django import forms
from django.utils.datastructures import SortedDict

from ecs.core.models import ChecklistBlueprint, Checklist, ChecklistAnswer, ChecklistQuestion


def make_checklist_form(checklist):
    fields = SortedDict()
    blueprint = checklist.blueprint
    i = 0
    for question in blueprint.questions.order_by('text'):
        i = i + 1
        answer = checklist.answers.get(question=question)
        fields['q%s' % i] = forms.NullBooleanField(initial=answer.answer, label=question.text, help_text=question.description, required=False)
        fields['c%s' % i] = forms.CharField(initial=answer.comment, label='Kommentar', required=False)
    form_class = type('Checklist%sForm' % blueprint.pk, (forms.BaseForm,), {'base_fields': fields})
    return form_class

