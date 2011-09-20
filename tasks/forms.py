# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.tasks.models import TaskType
from ecs.core.forms.fields import MultiselectWidget

class DeclineTaskForm(forms.Form):
    message = forms.CharField(required=False)
    

TASK_MANAGEMENT_CHOICES = [('delegate', _('delegate')),('message', _('message'))]
TASK_QUESTION_TYPE = [('callback', _('callback')), ('somebody', _('somebody')), ('related', _('related') )]

class TaskChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, task):
        return u"%s (%s)" % (task.assigned_to, task)

class ManageTaskForm(forms.Form):
    action = forms.ChoiceField(choices=TASK_MANAGEMENT_CHOICES)
    assign_to = forms.ModelChoiceField(queryset=User.objects.all().order_by('last_name', 'first_name', 'email'), required=False, empty_label=_('<group>'))
    
    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task')
        self.task = task
        super(ManageTaskForm, self).__init__(*args, **kwargs)
        fs = self.fields
        fs['callback_task'] = TaskChoiceField(queryset=task.trail, required=False)
        fs['related_task'] = TaskChoiceField(queryset=task.related_tasks.exclude(assigned_to=None).exclude(pk=task.pk), required=False)
        fs['assign_to'].queryset = fs['assign_to'].queryset.filter(groups__task_types=task.task_type)
        if task.choices:
            fs['action'].choices += [('complete_%s' % i, choice[i]) for i, choice in enumerate(task.choices)]
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
                self._errors['assign_to'] = self.error_class([_(u'You must select a user.')])

        return cd

class TaskTypeMultipleChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        from django.utils.encoding import force_unicode
        if self.required and not value:
            raise forms.ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise forms.ValidationError(self.error_messages['list'])
        for uid in value:
            try:
                self.queryset.filter(workflow_node__uid=uid)
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid_pk_value'] % pk)
        qs = self.queryset.filter(workflow_node__uid__in=value)
        uids = set([force_unicode(o.workflow_node.uid) for o in qs])
        for val in value:
            if force_unicode(val) not in uids:
                raise forms.ValidationError(self.error_messages['invalid_choice'] % val)
        return qs

class TaskListFilterForm(forms.Form):
    amg = forms.BooleanField(required=False)
    mpg = forms.BooleanField(required=False)
    thesis = forms.BooleanField(required=False)
    expedited = forms.BooleanField(required=False)
    other = forms.BooleanField(required=False)

    mine = forms.BooleanField(required=False)
    assigned = forms.BooleanField(required=False)
    open = forms.BooleanField(required=False)
    proxy = forms.BooleanField(required=False)

    sorting = forms.ChoiceField(required=False, choices=(
        ('deadline', _('Deadline')),
        ('oldest', _('Oldest')),
        ('newest', _('Newest')),
    ))

    task_types = TaskTypeMultipleChoiceField(required=False, queryset=TaskType.objects.all())

    def __init__(self, *args, **kwargs):
        super(TaskListFilterForm, self).__init__(*args, **kwargs)
        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['task_types'].widget = MultiselectWidget(url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'task_types'}))
