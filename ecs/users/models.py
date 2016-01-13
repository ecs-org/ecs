import uuid

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django_extensions.db.fields.json import JSONField
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    last_password_change = models.DateTimeField(auto_now_add=True)
    is_phantom = models.BooleanField(default=False)
    is_indisposed = models.BooleanField(default=False)
    communication_proxy = models.ForeignKey(User, null=True)

    is_board_member = models.BooleanField(default=False)
    is_executive_board_member = models.BooleanField(default=False)
    is_thesis_reviewer = models.BooleanField(default=False)
    is_insurance_reviewer = models.BooleanField(default=False)
    is_expedited_reviewer = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=False)
    is_resident_member = models.BooleanField(default=False)
    is_help_writer = models.BooleanField(default=False)
    is_testuser = models.BooleanField(default=False)
    is_developer = models.BooleanField(default=False)

    session_key = models.CharField(max_length=40, null=True)
    single_login_enforced = models.BooleanField(default=False)

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

    def __str__(self):
        return str(self.user)

    def get_single_login_enforced(self):
        if self.single_login_enforced:
            self.single_login_enforced = False
            self.save()
            return True
        else:
            return False

    def has_explicit_workflow(self):
        return self.user.groups.exclude(name__in=['External Reviewer', 'userswitcher_target', 'translators']).exists()

class UserSettings(models.Model):
    user = models.OneToOneField(User, related_name='ecs_settings')
    submission_filter_search = JSONField()
    submission_filter_all = JSONField()
    submission_filter_widget = JSONField()
    submission_filter_widget_internal = JSONField()
    submission_filter_mine = JSONField()
    submission_filter_assigned = JSONField()
    task_filter = models.TextField(null=True)
    communication_filter = JSONField()
    useradministration_filter = JSONField()

def _post_user_save(sender, **kwargs):
    # XXX: 'raw' is passed during fixture loading, but that's an undocumented feature - see django bug #13299 (FMD1)
    if kwargs['created'] and not kwargs.get('raw'):
        UserProfile.objects.create(user=kwargs['instance'])
        UserSettings.objects.create(user=kwargs['instance'])

post_save.connect(_post_user_save, sender=User)


class InvitationQuerySet(models.QuerySet):
    def new(self):
        return self.filter(is_accepted=False)

class InvitationManager(models.Manager):
    def get_queryset(self):
        # XXX: We really shouldn't be using distinct() here - it hurts
        # performance. Also, it prevents us from simply replacing the
        # InvitationManager with InvitationQuerySet.as_manager().
        return InvitationQuerySet(self.model).distinct()

    def new(self):
        return self.all().new()

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
