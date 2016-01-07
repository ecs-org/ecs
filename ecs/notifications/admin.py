from django.contrib import admin
from ecs.notifications.models import NotificationType, Notification

admin.site.register(NotificationType)
admin.site.register(Notification)
