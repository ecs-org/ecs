# -*- coding: utf-8 -*-
from django.contrib import admin
from ecs.documents.models import DocumentType, Document

admin.site.register(DocumentType)
admin.site.register(Document)
