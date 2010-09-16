# -*- coding: utf-8 -*-

import threading

from django.contrib.sessions.models import Session

from ecs.users.models import UserProfile


class SingleLogin(object):
    def process_request(self, request):
        """
        If active, users can only have one active session. This prevents
        account sharing and opening the site in two browsers.
        """

        if not request.user.is_authenticated():
            return

        current_session = Session.objects.get(session_key=request.session.session_key)
        profile = request.user.ecs_profile

        if profile.session_key == current_session.session_key:
            return

        old_session_key = profile.session_key
        profile.session_key = current_session.session_key
        profile.save()

        if old_session_key and Session.objects.filter(session_key=old_session_key):
            Session.objects.filter(session_key=old_session_key).delete()
            request.single_login_enforced = True


current_user_store = threading.local()

class GlobalUserMiddleware(object):
    def process_request(self, request):
        if request.user:
            current_user_store.user = request.user
        return None
    
    def process_response(self, request, response):
        if hasattr(current_user_store, 'user'):
            del current_user_store.user
        return response
    
    def process_exception(self, request, exception):
        if hasattr(current_user_store, 'user'):
            del current_user_store.user
        return None

