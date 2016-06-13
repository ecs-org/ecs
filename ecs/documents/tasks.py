from datetime import timedelta

from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Count
from django.contrib.auth.models import User

from celery.task import periodic_task
from celery.schedules import crontab

from ecs.documents.models import DownloadHistory
from ecs.communication.utils import send_message
from ecs.users.utils import get_user, get_office_user, get_full_name


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
        print(user_id, count)
        user = User.objects.get(id=user_id)
        subject = _('Large number of downloads by {user}').format(
            user=get_full_name(user))
        text = _('{user} has downloaded {count} documents during the last week.').format(
            user=get_full_name(user), count=count)
        send_message(sender, receiver, subject, text)
