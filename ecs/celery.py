import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecs.settings')
from django.conf import settings

app = Celery('ecs.celery')
app.config_from_object('django.conf:settings')
