from django.apps import AppConfig


class IntegrationAppConfig(AppConfig):
    name = 'ecs.integration'

    def ready(self):
        # XXX: should be imported in the AppConfig of the respective app itself
        import ecs.core.triggers
        import ecs.votes.triggers
        import ecs.notifications.triggers
        import ecs.meetings.triggers

        # Patch the user __str__ method, so the hash in the username field
        # does not show up.
        # XXX: We should be using a custom user model instead.
        from django.contrib.auth.models import User
        from ecs.users.utils import get_full_name
        User.__str__ = get_full_name
