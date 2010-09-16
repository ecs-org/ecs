# -*- coding: utf-8 -*-

from uuid import uuid4

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class AuditTrail(models.Model):
    #instance = generic.GenericForeignKey(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100, null=False, blank=False)
    user = models.ForeignKey(User)
    diff = models.TextField()

    def __unicode__(self):
        line = '[%s] %s\n' % (self.created_at.strftime('%b %d %Y %H:%M:%S'), self.description)
        line += '    User: %s %s (%s) <%s>\n' % (self.user.first_name, self.user.last_name, self.user.username, self.user.email)
        line += '    == diff start ==\n%s\n    == diff end ==\n' % self.diff
        return line

    def save(self, *args, **kwargs):
        rval = super(AuditTrail, self).save(*args, **kwargs)
        print unicode(self)
        # TODO: log with rsyslogd
        return rval
