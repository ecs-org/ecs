# -*- coding: utf-8 -*-
import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.utils.functional import wraps
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db import transaction

from ecs.users.middleware import current_user_store
from ecs.users.models import Invitation
from ecs.ecsmail.mail import deliver
from ecs.utils.viewutils import render_html


def hash_email(email):
    return hashlib.md5(email.lower()).hexdigest()[:30]

def get_or_create_user(email, defaults=None):
    if defaults is None:
        defaults = {}

    return User.objects.get_or_create(username=hash_email(email), email=email, defaults=defaults)

def create_user(email, **kwargs):
    return User.objects.create(username=hash_email(email), email=email, **kwargs)

def get_user(email, **kwargs):
    return User.objects.get(username=hash_email(email), **kwargs)

def get_current_user():
    if hasattr(current_user_store, 'user'):
        return current_user_store.user
    else:
        return None
        
class sudo(object):
    def __init__(self, user=None):
        self.user = user

    def __enter__(self):
        from ecs.users.middleware import current_user_store
        self._previous_user = getattr(current_user_store, 'user', None)
        user = self.user
        if callable(user):
            user = user()
        current_user_store.user = user
        
    def __exit__(self, *exc):
        from ecs.users.middleware import current_user_store
        current_user_store.user = self._previous_user
        
    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return decorated


def user_flag_required(flag):
    return user_passes_test(lambda u: getattr(u.ecs_profile, flag, False))

def user_group_required(group):
    return user_passes_test(lambda u: bool(u.groups.filter(name=group).count()))

def invite_user(request, email):
    comment = None
    try:
        sid = transaction.savepoint()
        user, created = get_or_create_user(email)
        if not created:
            raise ValueError(_(u'There is already a user with this email address.'))
        user.ecs_profile.phantom = True
        user.ecs_profile.save()

        invitation = Invitation.objects.create(user=user)

        subject = _(u'ECS account creation')
        link = request.build_absolute_uri(reverse('ecs.users.views.accept_invitation', kwargs={'invitation_uuid': invitation.uuid}))
        htmlmail = unicode(render_html(request, 'users/invitation/invitation_email.html', {
            'link': link,
        }))
        transferlist = deliver(subject, None, settings.DEFAULT_FROM_EMAIL, email, message_html=htmlmail)
        try:
            msgid, rawmail = transferlist[0]
            print rawmail
        except IndexError:
            raise ValueError(_(u'The email could not be delivered.'))
    except ValueError, e:
        transaction.savepoint_rollback(sid)
        comment = unicode(e)
    except Exception, e:
        transaction.savepoint_rollback(sid)
        raise e
    else:
        transaction.savepoint_commit(sid)
        comment = _(u'The user has been invited.')

    return comment

