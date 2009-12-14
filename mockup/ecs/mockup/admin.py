from django.contrib import admin
from ecs.mockup.models import Mockup

admin.site.register(Mockup, admin.ModelAdmin)
