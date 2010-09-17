# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.conf import settings

from ecs.audit.signals import post_save_handler

post_save.connect(post_save_handler)
