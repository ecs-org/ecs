from django import forms
from django.utils.datastructures import SortedDict

from ecs.core.models import ChecklistBlueprint, Checklist, ChecklistAnswer, ChecklistQuestion


def make_checklist_form(checklist):
    fields = SortedDict()
    blueprint = checklist.blueprint
    i = 0
    for question in blueprint.questions.order_by('id'):
        i = i + 1
        answer = checklist.answers.get(question=question)
        fields['f_%s_q' % i] = forms.NullBooleanField(initial=answer.answer, label='%s. %s' % (i, question.text), help_text=question.description, required=False)
        fields['f_%s_c' % i] = forms.CharField(label='Kommentar', required=False)
    form_class = type('Checklist%sForm' % blueprint.pk, (forms.BaseForm,), {'base_fields': fields})
    return form_class
