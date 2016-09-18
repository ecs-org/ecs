from django.dispatch import receiver
from django.utils.translation import ugettext as _

from ecs.notifications import signals
from ecs.notifications.models import NotificationAnswer
from ecs.users.utils import get_current_user


@receiver(signals.on_notification_submit)
def on_notification_submit(sender, **kwargs):
    notification = kwargs['notification']
    notification.render_pdf_document()
    

@receiver(signals.on_safety_notification_review)
def on_safety_notification_review(sender, **kwargs):
    notification = kwargs['notification']
    notification = notification.safetynotification
    notification.is_acknowledged = True
    notification.reviewer = get_current_user()
    notification.save()

    # automatically create notification answer
    answer = NotificationAnswer.objects.create(notification=notification, is_final_version=True, text=_('Die Ethikkommission bestätigt den Erhalt der Sicherheitsmeldung.'))
