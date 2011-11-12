from datetime import datetime, timedelta
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ecs.utils import cached_property
from ecs.workflow.models import Token, Node
from ecs.workflow.signals import token_received, token_consumed
from ecs.authorization.managers import AuthorizationManager

class TaskType(models.Model):
    name = models.CharField(max_length=100)
    workflow_node = models.OneToOneField(Node, null=True)
    groups = models.ManyToManyField(Group, related_name='task_types', blank=True)
    
    def __unicode__(self):
        if self.name:
            return _(self.name)
        elif self.workflow_node_id:
            return u'TaskType for %s' % self.workflow_node
        return u'TaskType <Anonymous>'

    @property
    def trans_name(self):
        return _(self.name)

class TaskQuerySet(models.query.QuerySet):
    def for_data(self, data):
        ct = ContentType.objects.get_for_model(type(data))
        return self.filter(content_type=ct, data_id=data.pk)
        
    def open(self):
        return self.filter(deleted_at__isnull=True, closed_at=None)
        
    def mark_deleted(self):
        return self.update(deleted_at=datetime.now())

    def acceptable_for_user(self, user):
        return self.filter(models.Q(assigned_to=None) | models.Q(assigned_to=user, accepted=False) | models.Q(assigned_to__ecs_profile__is_indisposed=True)).exclude(deleted_at__isnull=False)

    def for_user(self, user, activity=None, data=None):
        qs = self.filter(models.Q(task_type__groups__user=user) | models.Q(task_type__groups__isnull=True)).exclude(deleted_at__isnull=False)
        if activity:
            qs = qs.filter(workflow_token__node__node_type=activity._meta.node_type)
        if data:
            ct = ContentType.objects.get_for_model(type(data))
            qs = qs.filter(content_type=ct, data_id=data.pk)
        return qs

    def for_widget(self, user):
        not_for_widget = ['resubmission', 'b2_resubmission', 'external_review', 'paper_submission_review', 'thesis_paper_submission_review']
        return self.for_user(user).exclude(task_type__workflow_node__uid__in=not_for_widget)

    def for_submission(self, submission, related=True):
        # local import to prevent circular import
        from ecs.core.models import Submission
        from ecs.votes.models import Vote
        from ecs.meetings.models import Meeting
        from ecs.checklists.models import Checklist
        from ecs.notifications.models import Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification, SafetyNotification

        tasks = self.all()
        submission_ct = ContentType.objects.get_for_model(Submission)
        q = models.Q(content_type=submission_ct, data_id=submission.pk)
        if related:
            vote_ct = ContentType.objects.get_for_model(Vote)
            q |= models.Q(content_type=vote_ct, data_id__in=Vote.objects.filter(submission_form__submission=submission).values('pk').query)

            meeting_ct = ContentType.objects.get_for_model(Meeting)
            q |= models.Q(content_type=meeting_ct, data_id__in=submission.meetings.values('pk').query)

            for notification_model in (Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification, SafetyNotification):
                notification_ct = ContentType.objects.get_for_model(notification_model)
                q |= models.Q(content_type=notification_ct, data_id__in=notification_model.objects.filter(submission_forms__submission=submission).values('pk').query)
            
            checklist_ct = ContentType.objects.get_for_model(Checklist)
            q |= models.Q(content_type=checklist_ct, data_id__in=Checklist.objects.filter(submission=submission).values('pk').query)
            
        return self.filter(q).distinct()

class TaskManager(AuthorizationManager):
    def get_base_query_set(self):
        return TaskQuerySet(self.model).distinct()

    def for_data(self, data):
        return self.all().for_data(data)

    def acceptable_for_user(self, user):
        return self.all().acceptable_for_user(user)

    def for_user(self, *args, **kwargs):
        return self.all().for_user(*args, **kwargs)

    def for_widget(self, user):
        return self.all().for_widget(user)

    def for_submission(self, submission, related=True):
        return self.all().for_submission(submission, related=related)
        
    def open(self):
        return self.all().open()

class Task(models.Model):
    task_type = models.ForeignKey(TaskType, related_name='tasks')
    workflow_token = models.OneToOneField(Token, null=True, related_name='task')
    content_type = models.ForeignKey(ContentType, null=True)
    data_id = models.PositiveIntegerField(null=True)
    data = GenericForeignKey(ct_field='content_type', fk_field='data_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, related_name='created_tasks')

    assigned_at = models.DateTimeField(null=True)
    assigned_to = models.ForeignKey(User, null=True, related_name='tasks')
    closed_at = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    
    accepted = models.BooleanField(default=False)

    expedited_review_categories = models.ManyToManyField('core.ExpeditedReviewCategory')
    
    objects = TaskManager()

    def save(self, *args, **kwargs):
        rval = super(Task, self).save(*args, **kwargs)
        if self.workflow_token and not self.workflow_token.deadline:
            self.workflow_token.deadline = datetime.now() + timedelta(days=30)
            self.workflow_token.save()
        return rval

    def get_preview_url(self):
        from ecs.core.models import Submission
        from ecs.votes.models import Vote
        from ecs.notifications.models import Notification

        if isinstance(self.data, Notification):
            return reverse('ecs.notifications.views.view_notification', kwargs={'notification_pk': self.data.pk})

        submission_form = None
        if self.content_type == ContentType.objects.get_for_model(Submission):
            submission_form = self.data.current_submission_form
        elif self.content_type == ContentType.objects.get_for_model(Vote):
            submission_form = self.data.submission_form
        if submission_form:
            return reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk})
        else:
            return None

    @property
    def managed_transparently(self):
        return self.task_type.workflow_node.uid in ['resubmission', 'b2_resubmission', 'external_review']

    @property
    def is_locked(self):
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
        
    def get_final_urls(self):
        if not self.node_controller:
            return []
        return self.node_controller.get_final_urls()
    
    @property
    def choices(self):
        if not self.node_controller:
            return None
        return self.node_controller.get_choices()
    
    def close(self, commit=True):
        self.closed_at = datetime.now()
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
            
    def reopen(self, user=None):
        assert self.closed_at is not None
        new = type(self)()
        for attr in ('task_type', 'content_type', 'data_id'):
            setattr(new, attr, getattr(self, attr))
        new.workflow_token = self.node_controller.activate()
        user = user or self.assigned_to
        new.created_by = user
        new.accept(user=user, check_authorization=False, commit=False)
        new.save()
        return new
        
    def assign(self, user, check_authorization=True, commit=True):
        if user and check_authorization:
            groups = self.task_type.groups.all()
            if groups and not user.groups.filter(pk__in=[g.pk for g in groups])[:1]:
                raise ValueError((u"Task %s cannot be assigned to user %s, it requires one of the following groups: %s" % (
                    self, 
                    user, 
                    ", ".join(unicode(x) for x in self.task_type.groups.all()),
                )).encode('ascii', 'ignore'))
        self.assigned_to = user
        self.accepted = False
        if user:
            self.assigned_at = datetime.now()
        else:
            self.assigned_at = None
        if commit:
            self.save()
        
    def accept(self, user=None, commit=True, check_authorization=True):
        if user:
            self.assign(user, commit=False, check_authorization=check_authorization)
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
    if sender.repeated:
        return
    try:
        task_type = TaskType.objects.get(workflow_node=sender.node)
        Task.objects.create(workflow_token=sender, task_type=task_type, data=sender.workflow.data)
    except TaskType.DoesNotExist:
        pass

def workflow_token_consumed(sender, **kwargs):
    for task in Task.objects.filter(workflow_token=sender, closed_at__isnull=True):
        task.close()

def node_saved(sender, **kwargs):
    node, created = kwargs['instance'], kwargs['created']
    if not created or not node.node_type.is_activity:
        return
    name = node.name or node.node_type.name or node.node_type.implementation
    task_type, created = TaskType.objects.get_or_create(workflow_node=node, name=name)
        
token_received.connect(workflow_token_received)
token_consumed.connect(workflow_token_consumed)
post_save.connect(node_saved, sender=Node)
