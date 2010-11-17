import datetime
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core.urlresolvers import reverse

from ecs.utils import cached_property
from ecs.workflow.models import Token, Node
from ecs.workflow.signals import token_received, token_consumed
from ecs.core.models import Submission

class TaskType(models.Model):
    name = models.CharField(max_length=100)
    workflow_node = models.OneToOneField(Node, null=True)
    groups = models.ManyToManyField(Group, related_name='task_types', blank=True)
    
    def __unicode__(self):
        if self.name:
            return self.name
        elif self.workflow_node_id:
            return u'TaskType for %s' % self.workflow_node
        return u'TaskType <Anonymous>'
    
class TaskManager(models.Manager):
    def for_data(self, data):
        ct = ContentType.objects.get_for_model(type(data))
        return self.filter(content_type=ct, data_id=data.pk)
        
    def acceptable_for_user(self, user):
        return self.filter(models.Q(assigned_to=None) | models.Q(assigned_to=user, accepted=False) | models.Q(assigned_to__ecs_profile__indisposed=True))
        
    def for_user(self, user):
        return self.filter(models.Q(task_type__groups__user=user) | models.Q(task_type__groups__isnull=True))


class Task(models.Model):
    task_type = models.ForeignKey(TaskType, related_name='tasks')
    workflow_token = models.OneToOneField(Token, null=True, related_name='task')
    content_type = models.ForeignKey(ContentType, null=True)
    data_id = models.PositiveIntegerField(null=True)
    data = GenericForeignKey(ct_field='content_type', fk_field='data_id')
    
    created_at = models.DateTimeField(default=datetime.datetime.now)
    created_by = models.ForeignKey(User, null=True, related_name='created_tasks')

    assigned_at = models.DateTimeField(null=True)
    assigned_to = models.ForeignKey(User, null=True, related_name='tasks')
    closed_at = models.DateTimeField(null=True)
    
    accepted = models.BooleanField(default=False)
    
    objects = TaskManager()

    def save(self, *args, **kwargs):
        rval = super(Task, self).save(*args, **kwargs)
        if self.workflow_token and not self.workflow_token.deadline:
            self.workflow_token.deadline = datetime.datetime.now() + datetime.timedelta(days=30)
            self.workflow_token.save()
        return rval

    def get_preview_url(self):
        if self.content_type == ContentType.objects.get_for_model(Submission):
            return reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': self.data.current_submission_form.pk})
        else:
            return None

    @property
    def locked(self):
        if not self.workflow_token_id:
            return False
        return self.workflow_token.locked
    
    @cached_property
    def node_controller(self):
        if not self.workflow_token_id:
            return None
        return self.workflow_token.node.bind(self.workflow_token.workflow)
        
    @cached_property
    def url(self):
        if not self.node_controller:
            return None
        return self.node_controller.get_url()
    
    @property
    def choices(self):
        if not self.node_controller:
            return None
        return self.node_controller.get_choices()
    
    def close(self, commit=True):
        self.closed_at = datetime.datetime.now()
        if commit:
            self.save()
        
    def done(self, choice=None, user=None, commit=True):
        if user and self.assigned_to_id != user.id:
            self.assign(user)
        token = self.workflow_token
        if token:
            self.data.workflow.do(token, choice=choice)
        else:
            self.close(commit=commit)
        
    def assign(self, user, check_authorization=True, commit=True):
        if user and check_authorization:
            groups = self.task_type.groups.all()
            if groups and not user.groups.filter(pk__in=[g.pk for g in groups])[:1]:
                raise ValueError("Task %s cannot be assigned to user %s, it requires one of the following groups: %s" % (self, user, ", ".join(map(unicode, self.task_type.groups.all()))))
        self.assigned_to = user
        self.accepted = False
        if user:
            self.assigned_at = datetime.datetime.now()
        else:
            self.assigned_at = None
        if commit:
            self.save()
        
    def accept(self, user=None, commit=True):
        if user:
            self.assign(user, commit=False)
        self.accepted = True
        if commit:
            self.save()
        
    @property
    def trail(self):
        if not self.workflow_token:
            return Task.objects.none()
        return Task.objects.filter(workflow_token__in=self.workflow_token.activity_trail)
        
    @property
    def related_tasks(self):
        if not self.workflow_token:
            return Task.objects.none()
        return Task.objects.filter(workflow_token__workflow=self.workflow_token.workflow)
        
    def __unicode__(self):
        return u"%s %s" % (self.data, self.task_type)

# workflow integration:
def workflow_token_received(sender, **kwargs):
    try:
        task_type = TaskType.objects.get(workflow_node=sender.node)
        Task.objects.create(workflow_token=sender, task_type=task_type, data=sender.workflow.data)
    except TaskType.DoesNotExist:
        pass
    
def workflow_token_consumed(sender, **kwargs):
    try:
        task = Task.objects.get(workflow_token=sender)
        task.close()
    except Task.DoesNotExist:
        pass

def node_saved(sender, **kwargs):
    node, created = kwargs['instance'], kwargs['created']
    if not created or not node.node_type.is_activity:
        return
    name = node.name or node.node_type.name or node.node_type.implementation
    task_type, created = TaskType.objects.get_or_create(workflow_node=node, name=name)
        
token_received.connect(workflow_token_received)
token_consumed.connect(workflow_token_consumed)
post_save.connect(node_saved, sender=Node)
