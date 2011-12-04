#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.communication.utils import send_system_message_template
from ecs.notifications import signals
from ecs.notifications.models import NotificationAnswer
from ecs.utils import connect


@connect(signals.on_notification_submit)
def on_notification_submit(sender, **kwargs):
    notification = kwargs['notification']
    notification.render_pdf()
    

@connect(signals.on_safety_notification_review)
def on_safety_notification_review(sender, **kwargs):
    notification = kwargs['notification']
    notification = notification.safetynotification
    notification.is_acknowledged = True
    notification.save()

    # automatically create notification answer
    answer = NotificationAnswer.objects.create(notification=notification, is_final_version=True, text=_(u'Die Ethikkommission bestätigt den Erhalt der Sicherheitsmeldung.'))
