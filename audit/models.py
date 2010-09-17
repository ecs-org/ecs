# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime
import hmac
import hashlib

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.conf import settings

from ecs.users.utils import get_current_user

class AuditTrail(models.Model):
    instance = generic.GenericForeignKey()
    created_at = models.DateTimeField()
    description = models.CharField(max_length=100, null=False, blank=False)
    user = models.ForeignKey(User, null=False, blank=False)
    data = models.TextField(null=False, blank=False)
    hash = models.CharField(max_length=64, null=False, blank=False)

    def _get_log_line(self):
        line = '[%s] %s\n' % (self.created_at.strftime('%b %d %Y %H:%M:%S'), self.description)
        line += '    User: %s %s (%s) <%s>\n' % (self.user.first_name, self.user.last_name, self.user.username, self.user.email)
        line += '    == data start ==\n%s\n    == data end ==\n' % self.data
        return line
    
    def get_log_line(self):
        line = self._get_log_line()
        line += '    Hash: %s\n' % self.hash
        return line
    
    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        try:
            previous_entry = AuditTrail.objects.order_by('-created_at')[0]
        except IndexError:
            last_hash = ''
        else:
            last_hash = previous_entry.hash
        self.user = get_current_user()
        self.created_at = datetime.now()
        self.hash = hmac.new(str(last_hash), self._get_log_line(), hashlib.sha256).hexdigest()
        rval = super(AuditTrail, self).save(*args, **kwargs)
        if settings.DEBUG:
            print self.description
        # TODO: log with rsyslogd
        return rval
