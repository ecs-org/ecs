# -*- coding: utf-8 -*-
from urllib import urlencode

from django import forms
from django.http import QueryDict
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.tasks.models import TaskType
from ecs.core.forms.fields import MultiselectWidget
from ecs.users.utils import get_current_user

class DeclineTaskForm(forms.Form):
    message = forms.CharField(required=False)
    

class TaskChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, task):
        return u"%s (%s)" % (task.assigned_to, task)

class ManageTaskForm(forms.Form):
    action = forms.ChoiceField(choices=[])
    assign_to = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True).exclude(profile__is_testuser=True).order_by('last_name', 'first_name', 'email'), required=False, empty_label=_('<group>'))
    post_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task')
        self.task = task
        super(ManageTaskForm, self).__init__(*args, **kwargs)
        fs = self.fields
        fs['callback_task'] = TaskChoiceField(queryset=task.trail, required=False)
        fs['related_task'] = TaskChoiceField(queryset=task.related_tasks.exclude(assigned_to=None).exclude(pk=task.pk), required=False)
        if task.task_type.is_delegatable:
            fs['action'].choices = [('delegate', _('delegate')),('message', _('message'))]
            assign_to_q = fs['assign_to'].queryset.filter(groups__task_types=task.task_type).exclude(pk=get_current_user().pk)
            if task.expedited_review_categories.exists():
                assign_to_q = assign_to_q.filter(expedited_review_categories__pk__in=task.expedited_review_categories.values('pk').query)
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
                self._errors['assign_to'] = self.error_class([_(u'You must select a user.')])
        elif action == 'complete' and self.task and self.task.is_locked:
            self._errors['locked'] = self.error_class([_(u'Fill out the form completely to complete the task.')])
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
    past_meetings = forms.BooleanField(required=False, initial=True)
    next_meeting = forms.BooleanField(required=False, initial=True)
    upcoming_meetings = forms.BooleanField(required=False, initial=True)
    no_meeting = forms.BooleanField(required=False, initial=True)

    amg = forms.BooleanField(required=False, initial=True)
    mpg = forms.BooleanField(required=False, initial=True)
    thesis = forms.BooleanField(required=False, initial=True)
    expedited = forms.BooleanField(required=False, initial=True)
    local_ec = forms.BooleanField(required=False, initial=True)
    other = forms.BooleanField(required=False, initial=True)

    mine = forms.BooleanField(required=False, initial=True)
    assigned = forms.BooleanField(required=False, initial=True)
    open = forms.BooleanField(required=False, initial=True)
    proxy = forms.BooleanField(required=False, initial=True)

    sorting = forms.ChoiceField(required=False, choices=(
        ('deadline', _('Deadline')),
        ('oldest', _('Oldest')),
        ('newest', _('Newest')),
    ), initial='deadline')

    task_types = TaskTypeMultipleChoiceField(required=False, queryset=TaskType.objects.all())

    def __init__(self, *args, **kwargs):
        super(TaskListFilterForm, self).__init__(*args, **kwargs)
        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['task_types'].widget = MultiselectWidget(url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'task_types'}))

    @property
    def defaults(self):
        data = {'sorting': 'deadline'}
        for name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                data[name] = u'on'
        return QueryDict(urlencode(data))

    def get_data(self):
        if self.is_bound:
            return self.data
        else:
            return self.defaults

    def urlencode(self):
        return self.get_data().urlencode()
