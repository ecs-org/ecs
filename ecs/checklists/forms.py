from django import forms
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _

from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.forms.fields import NullBooleanField
from ecs.checklists.models import Checklist

def _unpickle(checklist_pk, args, kwargs):
    checklist = Checklist.objects.get(pk=checklist_pk)
    form_cls = make_checklist_form(checklist)
    return form_cls(*args, **kwargs)

class ChecklistFormPickleMixin(object):
    def __reduce__(self):
        kwargs = {'data': self.data or None, 'prefix': self.prefix, 'initial': self.initial}
        return (_unpickle, (self.__class__.checklist.pk, (), kwargs))

def make_checklist_form(checklist):
    fields = SortedDict()
    blueprint = checklist.blueprint
    for question in blueprint.questions.all().order_by('index'):
        answer = checklist.answers.get(question=question)
        fullquestion = u'{num}. {text}\n{desc}'.format(num=question.number, text=question.text, desc=question.description)
        fields['q%s' % question.index] = NullBooleanField(initial=answer.answer, label=fullquestion, help_text=fullquestion, required=False)
        fields['c%s' % question.index] = forms.CharField(initial=answer.comment, label=_('comment/reasoning'), required=question.requires_comment, widget=forms.Textarea())
    form_class = type('Checklist%sForm' % checklist.pk, (ChecklistFormPickleMixin, ReadonlyFormMixin, forms.BaseForm,), {'base_fields': fields})
    form_class.checklist = checklist
    return form_class
