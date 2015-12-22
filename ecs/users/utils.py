# -*- coding: utf-8 -*-
import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.utils.functional import wraps
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.http import HttpRequest

from ecs.users.middleware import current_user_store
from ecs.users.models import Invitation
from ecs.communication.mailutils import deliver_to_recipient
from ecs.utils.viewutils import render_html

# Do not import models here which depend on the AuthorizationManager, because
# the AuthorizationManager depends on this module. If you need to import a
# model, do it inside a function.


def hash_email(email):
    return hashlib.md5(email.lower()).hexdigest()[:30]

def get_or_create_user(email, defaults=None, **kwargs):
    if defaults is None:
        defaults = {}

    return User.objects.get_or_create(username=hash_email(email), email=email, defaults=defaults, **kwargs)

def create_user(email, **kwargs):
    return User.objects.create(username=hash_email(email), email=email, **kwargs)

def get_user(email, **kwargs):
    try:
        name = hash_email(email)
    except UnicodeEncodeError:
        raise User.DoesNotExist()
    return User.objects.get(username=name, **kwargs)

def get_current_user():
    if hasattr(current_user_store, 'user'):
        return current_user_store.user
    else:
        return None

def get_full_name(user):
    profile = user.profile
    if user.first_name or user.last_name:
        nameparts = [user.first_name, user.last_name]
        if profile.title:
            nameparts.insert(0, profile.title)
        if profile.gender:
            if profile.gender == 'f':
                nameparts.insert(0, force_unicode(_('Ms.')))
            if profile.gender == 'm':
                nameparts.insert(0, force_unicode(_('Mr.')))
        return u' '.join(nameparts)
    else:
        return unicode(user.email)

def get_formal_name(user):
    if user.first_name and user.last_name:
        return u'{0}, {1}'.format(user.last_name, user.first_name)
    else:
        return unicode(user.email)

class sudo(object):
    """
    Please note: sudo is not iterator save, so dont yield in a function
    or block which is decorated with sudo
    """

    def __init__(self, user=None):
        self.user = user

    def __enter__(self):
        self._previous_previous_user = getattr(current_user_store, '_previous_user', None)
        self._previous_user = getattr(current_user_store, 'user', None)
        user = self.user
        if callable(user):
            user = user()
        current_user_store._previous_user = self._previous_user
        current_user_store.user = user

    def __exit__(self, *exc):
        current_user_store._previous_user = self._previous_previous_user
        current_user_store.user = self._previous_user

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return decorated


def user_flag_required(*flags):
    def check(user):
        return any(getattr(user.profile, f, False) for f in flags)
    return user_passes_test(check)


def user_group_required(*groups):
    return user_passes_test(lambda u: u.groups.filter(name__in=groups).exists())


def create_phantom_user(email, role=None):
    user = create_user(email)
    profile = user.profile
    profile.is_phantom = True
    profile.forward_messages_after_minutes = 5
    profile.save()

    if not role == 'investigator':  # see #4808
        invitation = Invitation.objects.create(user=user)

        subject = 'Erstellung eines Zugangs zum ECS'
        link = '{0}{1}'.format(
            settings.ABSOLUTE_URL_PREFIX,
            reverse('ecs.users.views.accept_invitation',
                kwargs={'invitation_uuid': invitation.uuid.get_hex()})
        )
        htmlmail = unicode(render_html(HttpRequest(), 'users/invitation/invitation_email.html', {
            'link': link,
        }))
        msgid, rawmail = deliver_to_recipient(email, subject, None, settings.DEFAULT_FROM_EMAIL, message_html=htmlmail)

    return user

def get_office_user(submission=None):
    from ecs.tasks.models import Task
    from ecs.core.models import AdvancedSettings
    if submission is not None:
        with sudo():
            tasks = Task.objects.for_submission(submission).filter(task_type__groups__name=u'EC-Office').exclude(assigned_to=get_current_user()).closed().order_by('-closed_at')
            try:
                return tasks[0].assigned_to
            except IndexError:
                pass
    return AdvancedSettings.objects.get(pk=1).default_contact
