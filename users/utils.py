# -*- coding: utf-8 -*-
import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.utils.functional import wraps
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils.encoding import force_unicode
from django.http import HttpRequest

from ecs.users.middleware import current_user_store, current_user_store
from ecs.users.models import Invitation
from ecs.ecsmail.utils import deliver_to_recipient
from ecs.utils.viewutils import render_html

# Do not import models here which depend on the AuthorizationManager, because
# the AuthorizationManager depends on this module. If you need to import a
# model, do it inside a function.


def hash_email(email):
    return hashlib.md5(email.lower()).hexdigest()[:30]

def get_or_create_user(email, defaults=None, start_workflow=True, **kwargs):
    if defaults is None:
        defaults = {}

    user, created = User.objects.get_or_create(username=hash_email(email), email=email, defaults=defaults, **kwargs)
    
    if start_workflow:
        profile = user.get_profile()
        profile.start_workflow = True
        profile.save()

    return user, created

def create_user(email, start_workflow=True, **kwargs):
    user = User.objects.create(username=hash_email(email), email=email, **kwargs)

    if start_workflow:
        profile = user.get_profile()
        profile.start_workflow = True
        profile.save()

    return user

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
    profile = user.ecs_profile
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
        return any(getattr(user.get_profile(), f, False) for f in flags)
    return user_passes_test(check)


def user_group_required(*groups):
    return user_passes_test(lambda u: u.groups.filter(name__in=groups).exists())


def create_phantom_user(email, role=None):
    sid = transaction.savepoint()
    try:
        user = create_user(email)
        profile = user.get_profile()
        profile.is_phantom = True
        profile.save()

        invitation = Invitation.objects.create(user=user)

        subject = _(u'ECS account creation')
        link = '{0}{1}'.format(settings.ABSOLUTE_URL_PREFIX, reverse('ecs.users.views.accept_invitation', kwargs={'invitation_uuid': invitation.uuid}))
        htmlmail = unicode(render_html(HttpRequest(), 'users/invitation/invitation_email.html', {
            'link': link,
        }))
        msgid, rawmail = deliver_to_recipient(email, subject, None, settings.DEFAULT_FROM_EMAIL, message_html=htmlmail)
        #print rawmail
    except Exception, e:
        transaction.savepoint_rollback(sid)
        raise e
    else:
        transaction.savepoint_commit(sid)

    return user

def get_ec_user(submission=None):
    from ecs.tasks.models import Task
    if submission is not None:
        with sudo():
            workflow_tokens = submission.workflow.tokens.filter(consumed_at__isnull=False).values('pk').query
            tasks = Task.objects.filter(workflow_token__in=workflow_tokens, assigned_to__groups__name=u'EC-Office').exclude(assigned_to=get_current_user()).order_by('-closed_at')
        try:
            task = tasks[0]
        except IndexError:
            return get_user(settings.DEFAULT_CONTACT)
        else:
            return task.assigned_to
    else:
        return get_user(settings.DEFAULT_CONTACT)
