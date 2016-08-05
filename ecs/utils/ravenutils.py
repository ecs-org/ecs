from django.conf import settings

from raven.contrib.django.client import DjangoClient as RavenDjangoClient

class DjangoClient(RavenDjangoClient):
    def build_msg(self, *args, **kwargs):
        data = super().build_msg(*args, **kwargs)
        data['tags']['branch'] = settings.ECS_GIT_BRANCH
        data['extra']['version'] = settings.ECS_VERSION
        return data
