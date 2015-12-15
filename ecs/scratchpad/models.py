# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from ecs.core.models.submissions import Submission

from ecs.authorization import AuthorizationManager

class ScratchPad(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    text = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User)
    submission = models.ForeignKey(Submission, null=True)

    objects = AuthorizationManager()

    class Meta:
        unique_together = (('owner', 'submission'),)

    def is_empty(self):
        return not self.text
