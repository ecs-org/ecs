# -*- coding: utf-8 -*-

from django.contrib import admin
from ecs.docstash.models import DocStash, DocStashData

admin.site.register(DocStash)
admin.site.register(DocStashData)
