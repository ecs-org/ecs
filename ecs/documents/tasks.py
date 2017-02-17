from datetime import timedelta

from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Count
from django.contrib.auth.models import User

from celery.task import periodic_task
from celery.schedules import crontab

from ecs.documents.models import DownloadHistory
from ecs.communication.utils import send_message_template
from ecs.users.utils import get_user, get_office_user


WEEKLY_DOWNLOAD_THRESHOLD = 150


@periodic_task(run_every=crontab(day_of_week=0, hour=23, minute=59))
def send_download_warnings():
    now = timezone.now()

    hist = (
        DownloadHistory.objects
            .filter(user__profile__is_internal=False,
                downloaded_at__range=(now - timedelta(days=7), now))
            .order_by('user_id')
            .values_list('user_id')
            .annotate(Count('id'))
            .filter(id__count__gt=WEEKLY_DOWNLOAD_THRESHOLD)
    )

    sender = get_user('root@system.local')
    receiver = get_office_user()

    for user_id, count in hist:
        user = User.objects.get(id=user_id)
        subject = _('Large number of downloads by {user}').format(user=user)
        send_message_template(sender, receiver, subject,
            'documents/messages/download_warning.txt',
            {'user': user,'count': count})


@periodic_task(run_every=crontab(day_of_month=1, hour=0, minute=15))
def expire_download_history():
    DownloadHistory.objects.filter(
        downloaded_at__lt=timezone.now() - timedelta(days=365 * 3),
    ).delete()
