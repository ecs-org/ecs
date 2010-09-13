from django.contrib.sessions.models import Session

from ecs.core.models import UserProfile


class SingleLogin(object):
    def process_request(self, request):
        """
        If active, users can only have one active session
        """
        if not request.user.is_authenticated():
            return

        session = Session.objects.get(session_key=request.session.session_key)
        profile = request.user.ecs_profile

        if profile.session_key != session.session_key:
            old_session_key = profile.session_key
            profile.session_key = session.session_key
            profile.save()

            if old_session_key:
                Session.objects.filter(session_key=old_session_key).delete()


