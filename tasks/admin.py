# -*- coding: utf-8 -*-

from django.contrib import admin
from ecs.tasks.models import TaskType, Task

admin.site.register(TaskType)
admin.site.register(Task)

