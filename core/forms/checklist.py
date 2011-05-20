import re

from django import forms
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _

from ecs.core.models import ChecklistBlueprint, Checklist, ChecklistAnswer, ChecklistQuestion
from ecs.core.forms.utils import ReadonlyFormMixin

def make_checklist_form(checklist):
    fields = SortedDict()
    blueprint = checklist.blueprint

    questions = []
    for question in blueprint.questions.all():
        m = re.match(r'(\d+)(\w*)', question.number)
        questions.append(('{0:03}{1}'.format(int(m.group(1)), m.group(2)), question,))

    for i, question in sorted(questions, key=lambda x: x[0]):
        answer = checklist.answers.get(question=question)
        fullquestion = u'{num}. {text}\n{desc}'.format(num=question.number, text=question.text, desc=question.description)
        fields['q%s' % i] = forms.NullBooleanField(initial=answer.answer, label=fullquestion, help_text=fullquestion, required=False)
        fields['c%s' % i] = forms.CharField(initial=answer.comment, label=_('comment'), required=False, widget=forms.Textarea())
    form_class = type('Checklist%sForm' % blueprint.pk, (ReadonlyFormMixin, forms.BaseForm,), {'base_fields': fields})
    return form_class

