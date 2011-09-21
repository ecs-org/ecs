# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.core.models.submissions import Submission

class ScratchPad(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    text = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User)
    submission = models.ForeignKey(Submission, null=True)

    class Meta:
        unique_together = (('owner', 'submission'),)

    def is_empty(self):
        return not self.text
