from django.dispatch import Signal

on_notification_submit = Signal() # sender: Notification subclass, kwargs: notification
on_safety_notification_review = Signal() # sender: Notification subclass, kwargs: notification