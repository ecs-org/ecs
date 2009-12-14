from django.contrib import admin
from ecs.feedback.models import FeedbackComment

admin.site.register(FeedbackComment, admin.ModelAdmin)
