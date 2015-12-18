from django.apps import AppConfig


class WorkflowAppConfig(AppConfig):
    name = 'ecs.workflow'

    def ready(self):
        self.module.autodiscover()
