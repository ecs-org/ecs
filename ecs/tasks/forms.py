from urllib.parse import urlencode

from django import forms
from django.http import QueryDict
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ecs.tasks.models import TaskType


class DeclineTaskForm(forms.Form):
    message = forms.CharField(required=False)
    

class TaskChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, task):
        return "%s (%s)" % (task.assigned_to, task)

class ManageTaskForm(forms.Form):
    action = forms.ChoiceField(choices=[])
    assign_to = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True).order_by('last_name', 'first_name', 'email'), required=False, empty_label=_('<group>'))
    post_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task')
        self.task = task
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        fs = self.fields
        fs['callback_task'] = TaskChoiceField(queryset=task.trail, required=False)
        fs['related_task'] = TaskChoiceField(queryset=task.related_tasks.exclude(assigned_to=None).exclude(pk=task.pk), required=False)
        if task.task_type.is_delegatable:
            fs['action'].choices = [('delegate', _('delegate')),('message', _('message'))]
            assign_to_q = fs['assign_to'].queryset.filter(groups__task_types=task.task_type).exclude(pk=self.user.pk)
            if task.medical_category_id:
                assign_to_q = assign_to_q.filter(
                    medical_categories=task.medical_category_id)
            fs['assign_to'].queryset = assign_to_q
        else:
            fs['action'].choices = [('message', _('message'))]
            del fs['assign_to']
        if task.choices:
            fs['action'].choices += [('complete_%s' % i, choice[0]) for i, choice in enumerate(task.choices)]
        else:
            fs['action'].choices += [('complete', _('complete'))]
        
    def get_choice(self):
        if not hasattr(self, 'choice_index'):
            return None
        return self.task.choices[self.choice_index][0]
        
    def clean_action(self):
        action = self.cleaned_data.get('action')
        if action.startswith('complete'):
            try:
                self.choice_index = int(action.split('_')[1])
                action = 'complete'
            except (ValueError, IndexError):
                pass
        return action
    
    def clean(self):
        cd = self.cleaned_data
        action = cd.get('action')
        if action == 'delegate':
            if 'assign_to' not in cd:
                self.add_error('assign_to', _('You must select a user.'))
        elif action == 'complete' and self.task and self.task.is_locked:
            self.add_error('post_data',
                _('Fill out the form completely to complete the task.'))
        return cd

class TaskListFilterForm(forms.Form):
    past_meetings = forms.BooleanField(required=False, initial=True)
    next_meeting = forms.BooleanField(required=False, initial=True)
    upcoming_meetings = forms.BooleanField(required=False, initial=True)
    no_meeting = forms.BooleanField(required=False, initial=True)

    lane_board = forms.BooleanField(required=False, initial=True)
    lane_expedited = forms.BooleanField(required=False, initial=True)
    lane_retrospective_thesis = forms.BooleanField(required=False, initial=True)
    lane_localec = forms.BooleanField(required=False, initial=True)
    lane_none = forms.BooleanField(required=False, initial=True)

    amg = forms.BooleanField(required=False, initial=True)
    mpg = forms.BooleanField(required=False, initial=True)
    thesis = forms.BooleanField(required=False, initial=True)
    other = forms.BooleanField(required=False, initial=True)

    task_types = forms.ModelMultipleChoiceField(required=False,
        queryset=TaskType.objects
            .order_by('workflow_node__uid', '-pk')
            .distinct('workflow_node__uid')
    )

    @property
    def defaults(self):
        data = {}
        for name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                data[name] = 'on'
        return QueryDict(urlencode(data))

    def get_data(self):
        if self.is_bound:
            return self.data
        else:
            return self.defaults

    def urlencode(self):
        return self.get_data().urlencode()
