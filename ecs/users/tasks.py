from datetime import timedelta

from django.utils import timezone

from celery.task import periodic_task
from celery.schedules import crontab

from ecs.users.models import LoginHistory

# run once per month on the first day of the month at 0:20
@periodic_task(run_every=crontab(day_of_month=1, hour=0, minute=20))
def expire_login_history():
    LoginHistory.objects.filter(
        timestamp__lt=timezone.now() - timedelta(days=365 * 5),
    ).delete()
