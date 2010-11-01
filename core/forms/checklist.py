from django import forms
from django.utils.datastructures import SortedDict

from ecs.core.models import ChecklistBlueprint, Checklist, ChecklistAnswer, ChecklistQuestion
from ecs.core.forms.utils import ReadonlyFormMixin

def make_checklist_form(checklist):
    fields = SortedDict()
    blueprint = checklist.blueprint
    for i, question in enumerate(blueprint.questions.order_by('text')):
        answer = checklist.answers.get(question=question)
        fields['q%s' % i] = forms.NullBooleanField(initial=answer.answer, label=question.text, help_text=question.description, required=False)
        fields['c%s' % i] = forms.CharField(initial=answer.comment, label='Kommentar', required=False, widget=forms.Textarea())
    form_class = type('Checklist%sForm' % blueprint.pk, (ReadonlyFormMixin, forms.BaseForm,), {'base_fields': fields})
    return form_class

