import datetime
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

from ecs.workflow.models import Token, Node
from ecs.workflow.signals import token_created, token_consumed

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

class Task(models.Model):
    task_type = models.ForeignKey(TaskType, related_name='tasks')
    workflow_token = models.OneToOneField(Token, null=True)
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
    
    @property
    def locked(self):
        if not self.workflow_token_id:
            return False
        return self.workflow_token.locked
    
    def close(self, commit=True):
        self.closed_at = datetime.datetime.now()
        if commit:
            self.save()
        
    def done(self, user=None, commit=True):
        if self.assigned_to_id != user.id:
            self.assign(user)
        token = self.workflow_token
        if token:
            self.data.workflow.do(token)
        else:
            self.close(user=user, commit=commit)
        
    def assign(self, user, check_authorization=True, commit=True):
        if user and check_authorization:
            groups = self.task_type.groups.all()
            if groups and not user.groups.filter(pk__in=[g.pk for g in groups])[:1]:
                raise ValueError("Task %s cannot be assigned to user %s, it requires one of the following groups: %s" % (self, user, ", ".join(map(unicode, self.task_type.groups.all()))))
        self.assigned_to = user
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
            return set()
        return Task.objects.filter(workflow_token__in=self.workflow_token.activity_trail)

# workflow integration:
def workflow_token_created(sender, **kwargs):
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
    task_type, created = TaskType.objects.get_or_create(workflow_node=node)
        
token_created.connect(workflow_token_created)
token_consumed.connect(workflow_token_consumed)
post_save.connect(node_saved, sender=Node)