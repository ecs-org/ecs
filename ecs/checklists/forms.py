from datetime import timedelta

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from ecs.checklists.models import ChecklistAnswer
from ecs.core.forms.utils import ReadonlyFormSetMixin
from ecs.core.forms.fields import NullBooleanField
from ecs.tasks.models import TaskType


class ChecklistAnswerForm(forms.ModelForm):
    answer = NullBooleanField(required=False)

    class Meta:
        model = ChecklistAnswer
        fields = ('answer', 'comment')
        labels = {'comment': _('comment/reasoning')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        question = self.instance.question
        fullquestion = '{num}. {text}\n{desc}'.format(num=question.number,
            text=question.text, desc=question.description)
        self.fields['answer'].label = fullquestion
        self.fields['answer'].help_text = fullquestion


class BaseChecklistAnswerFormSet(ReadonlyFormSetMixin, forms.BaseModelFormSet):
    pass


ChecklistAnswerFormSet = forms.modelformset_factory(ChecklistAnswer,
    formset=BaseChecklistAnswerFormSet, extra=0, form=ChecklistAnswerForm)


class ChecklistTaskCreationForm(forms.Form):
    task_type = forms.ModelChoiceField(queryset=TaskType.objects.filter(
            is_dynamic=True, workflow_node__graph__auto_start=True
        ).order_by('workflow_node__uid'), label=_('Task Type'))
    send_message_on_close = forms.BooleanField(required=False,
        label=_('Notify me when the task has been completed'))
    reminder_message_timeout = forms.ChoiceField(choices=(
            (None, _('No')),
            (1, _('After one day')),
            (7, _('After one week')),
            (14, _('After two week')),
        ), required=False,
        label=_('Remember me when the task hasn\'t been done'))

    def clean_reminder_message_timeout(self):
        days = self.cleaned_data['reminder_message_timeout']
        if not days:
            return None
        return timedelta(days=int(days))


class ChecklistTaskCreationStage2Form(forms.Form):
    assign_to = forms.ModelChoiceField(queryset=User.objects.none(),
        required=False, label=_('Assign to'))

    def __init__(self, submission, task_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submission = submission

        queryset = task_type.group.user_set.filter(is_active=True).order_by(
            'last_name', 'first_name', 'email')
        self.fields['assign_to'].queryset = queryset
        if not task_type.is_delegatable:
            self.fields['assign_to'].required = True
        else:
            self.fields['assign_to'].empty_label = _('<group>')

    def clean_assign_to(self):
        assign_to = self.cleaned_data['assign_to']
        if assign_to:
            biased = self.submission.biased_board_members.filter(
                id=assign_to.id).exists()
            if biased:
                raise forms.ValidationError(_('This user is biased.'))
        return assign_to
