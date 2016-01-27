from datetime import timedelta

from django.db.models import Count
from django.contrib.auth.models import User
from django.utils import timezone

from celery.task import periodic_task

from ecs.tracking.models import Request

MAX_REQUEST_AGE = timedelta(days=31)
MAX_REQUESTS_PER_USER = 50

@periodic_task(run_every=timedelta(days=1))
def cleanup_requests():
    # first delete all requests older than MAX_REQUEST_AGE
    Request.objects.filter(timestamp__lt=timezone.now() - MAX_REQUEST_AGE).delete()
    
    # then delete any request in excess of MAX_REQUESTS_PER_USER
    for user in User.objects.annotate(request_count=Count('requests')).filter(request_count__gt=MAX_REQUESTS_PER_USER):
        pivot = user.requests.order_by('-timestamp')[MAX_REQUESTS_PER_USER - 1]
        user.requests.filter(timestamp__lt=pivot.timestamp).delete()