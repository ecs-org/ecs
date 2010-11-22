# -*- coding: utf-8 -*-
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

def invite_user(email):
    try:
        sid = transaction.savepoint()
        user = User.objects.create(username=email[:30], email=email)
        user.ecs_profile.phantom = True
        user.ecs_profile.save()

        invitation = Invitation.objects.create(user=user)

        subject = _(u'ECS account creation')
        link = reverse('ecs.users.views.accept_invitation', kwargs={'invitation_uuid': invitation.uuid})
        text = _(u'An user account on the ECS system has been created for you.\nTo accept the invitation visit: %s') % link
        html = _(u'<html><head></head><body>An user account on the ECS system has been created for you.\nTo accept the invitation visit <a href="%s">this link</a></body></html>') % link

        transferlist = deliver(subject, text, settings.DEFAULT_FROM_EMAIL, email, html_message=html)
        msgid, rawmail = transferlist[0]
        print 'Sent Invitation to %s msgid=%s' % (email, msgid)
        print rawmail
    except Exception, e:
        transaction.savepoint_rollback(sid)
        print 'Failed to send invitation to %s' % email
        raise e
    else:
        transaction.savepoint_commit(sid)

