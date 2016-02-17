import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecs.settings')
from django.conf import settings

if hasattr(settings, 'RAVEN_CONFIG'):
    import raven
    from raven.contrib.celery import register_signal, register_logger_signal
    client = raven.Client(**settings.RAVEN_CONFIG)
    register_logger_signal(client)
    register_signal(client)

app = Celery('ecs.celery')
app.config_from_object('django.conf:settings')
