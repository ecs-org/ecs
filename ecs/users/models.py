import uuid

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django_extensions.db.fields.json import JSONField
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    last_password_change = models.DateTimeField(auto_now_add=True)
    is_phantom = models.BooleanField(default=False)
    is_indisposed = models.BooleanField(default=False)
    communication_proxy = models.ForeignKey(User, null=True)

    # denormalized from user groups for faster lookup
    is_board_member = models.BooleanField(default=False)
    is_resident_member = models.BooleanField(default=False)
    is_omniscient_member = models.BooleanField(default=False)
    is_executive = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=False)
    can_have_tasks = models.BooleanField(default=False)
    can_have_open_tasks = models.BooleanField(default=False)

    # XXX: not backed by user groups
    is_testuser = models.BooleanField(default=False)

    session_key = models.CharField(max_length=40, null=True)

    gender = models.CharField(max_length=1, choices=(('f', _('Ms')), ('m', _('Mr'))))
    title = models.CharField(max_length=30, blank=True)
    organisation = models.CharField(max_length=180, blank=True)
    jobtitle = models.CharField(max_length=130, blank=True)
    swift_bic = models.CharField(max_length=11, blank=True)
    iban = models.CharField(max_length=40, blank=True)

    address1 = models.CharField(max_length=60, blank=True)
    address2 = models.CharField(max_length=60, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=45, blank=True)

    social_security_number = models.CharField(max_length=10, blank=True)

    # 0 = never send messages, is editable via profile, activate via registration sets this to 5 minutes
    forward_messages_after_minutes = models.PositiveIntegerField(null=False, blank=False, default=0)

    task_uids = ArrayField(models.CharField(max_length=100), default=list)

    def __str__(self):
        return str(self.user)

    def update_flags(self):
        groups = set(self.user.groups.values_list('name', flat=True))
        self.is_board_member = 'Board Member' in groups
        self.is_resident_member = 'Resident Board Member' in groups
        self.is_omniscient_member = 'Omniscient Board Member' in groups
        self.is_executive = 'EC-Executive' in groups
        self.is_internal = bool(groups & {
            'EC-Executive',
            'EC-Office',
            'EC-Signing',
        })
        self.can_have_tasks = bool(groups & {
            'Board Member',
            'EC-Executive',
            'EC-Office',
            'EC-Signing',
            'GCP Reviewer',
            'Insurance Reviewer',
            'Statistic Reviewer',
            'External Reviewer',
            'Specialist'
        })
        self.can_have_open_tasks = bool(groups & {
            'Board Member',
            'EC-Executive',
            'EC-Office',
            'EC-Signing',
            'GCP Reviewer',
            'Insurance Reviewer',
            'Statistic Reviewer',
        })

    @property
    def show_task_widget(self):
        tasks = self.user.tasks(manager='unfiltered').open().for_widget()
        return self.can_have_tasks or tasks.exists()


class UserSettings(models.Model):
    user = models.OneToOneField(User, related_name='ecs_settings')
    submission_filter_search = JSONField()
    submission_filter_all = JSONField()
    submission_filter_widget = JSONField()
    submission_filter_widget_internal = JSONField()
    submission_filter_mine = JSONField()
    submission_filter_assigned = JSONField()
    task_filter = models.TextField(null=True)
    useradministration_filter = JSONField()

@receiver(post_save, sender=User)
def _post_user_save(sender, **kwargs):
    # XXX: 'raw' is passed during fixture loading, but that's an undocumented feature - see django bug #13299 (FMD1)
    if kwargs['created'] and not kwargs.get('raw'):
        UserProfile.objects.create(user=kwargs['instance'])
        UserSettings.objects.create(user=kwargs['instance'])


class InvitationQuerySet(models.QuerySet):
    def new(self):
        return self.filter(is_accepted=False)

class InvitationManager(models.Manager.from_queryset(InvitationQuerySet)):
    def get_queryset(self):
        # XXX: We really shouldn't be using distinct() here - it hurts
        # performance.
        return InvitationQuerySet(self.model).distinct()

class Invitation(models.Model):
    user = models.ForeignKey(User, related_name='ecs_invitations')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    is_accepted = models.BooleanField(default=False)

    objects = InvitationManager()


LOGIN_HISTORY_TYPES = (
    ('login', _('login')),
    ('logout', _('logout')),
)

class LoginHistory(models.Model):
    type = models.CharField(max_length=32, choices=LOGIN_HISTORY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    ip = models.GenericIPAddressField(protocol='ipv4')
