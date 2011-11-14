# -*- coding: utf-8 -*-
from datetime import datetime
import hmac
import hashlib

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from ecs.authorization import AuthorizationManager


class AuditTrailManager(AuthorizationManager):
    def get_last_change(self):
        try:
            return self.order_by('-created_at')[0]
        except IndexError:
            return None
    
    def get_previous_change_for_instance(self, instance, before_datetime=None):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        query = Q(object_id=instance.id, content_type=content_type)
        if before_datetime:
            query &= Q(created_at__lt=before_datetime)
        try:
            return self.filter(query).order_by('-created_at')[0]
        except IndexError:
            return None
    
class AuditTrail(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    instance = generic.GenericForeignKey()
    created_at = models.DateTimeField()
    description = models.CharField(max_length=100, null=False, blank=False)
    user = models.ForeignKey('auth.User', null=False, blank=False)
    data = models.TextField(null=False, blank=False)
    hash = models.CharField(max_length=64, null=False, blank=False)
    is_instance_created = models.BooleanField(default=False)

    objects = AuditTrailManager()

    @property
    def old_data(self):
        last_change = AuditTrail.objects.get_previous_change_for_instance(self.instance, self.created_at)
        if last_change:
            return last_change.data
        else:
            return ''

    def _get_log_line(self):
        line = u'[%s] %s\n' % (self.created_at.strftime('%b %d %Y %H:%M:%S'), self.description)
        line += u'    User: %s %s (%s) <%s>\n' % (self.user.first_name, self.user.last_name, self.user.username, self.user.email)
        line += u'>>>> old data\n%s\n====\n%s\n<<<< new data\n' % (self.old_data, self.data)
        return line
    
    def get_log_line(self):
        line = self._get_log_line()
        line += u'    Hash: %s\n' % self.hash
        return line
    
    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        previous_entry = AuditTrail.objects.get_last_change()
        if previous_entry:
            last_hash = previous_entry.hash
        else:
            last_hash = ''
        
        self.created_at = datetime.now()
        self.hash = hmac.new(str(last_hash), self._get_log_line().encode('utf8'), hashlib.sha256).hexdigest()
        rval = super(AuditTrail, self).save(*args, **kwargs)
        # TODO: log with rsyslogd
        return rval
