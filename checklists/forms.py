import re

from django import forms
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _

from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.forms.fields import NullBooleanField

def make_checklist_form(checklist):
    fields = SortedDict()
    blueprint = checklist.blueprint

    for question in blueprint.questions.all().order_by('index'):
        answer = checklist.answers.get(question=question)
        fullquestion = u'{num}. {text}\n{desc}'.format(num=question.number, text=question.text, desc=question.description)
        fields['q%s' % question.index] = NullBooleanField(initial=answer.answer, label=fullquestion, help_text=fullquestion, required=False)
        fields['c%s' % question.index] = forms.CharField(initial=answer.comment, label=_('comment/reasoning'), required=question.requires_comment, widget=forms.Textarea())
    form_class = type('Checklist%sForm' % blueprint.pk, (ReadonlyFormMixin, forms.BaseForm,), {'base_fields': fields})
    return form_class
