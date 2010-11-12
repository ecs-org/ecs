# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class EthicsCommission(models.Model):
    uuid = models.CharField(max_length=32)
    name = models.CharField(max_length=120)
    address_1 = models.CharField(max_length=120)
    address_2 = models.CharField(max_length=120)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=80)
    contactname = models.CharField(max_length=120, null=True)
    chairperson = models.CharField(max_length=120, null=True)
    email = models.EmailField(null=True)
    url = models.URLField(null=True)
    phone = models.CharField(max_length=60, null=True)
    fax = models.CharField(max_length=60, null=True)
    
    class Meta:
        app_label = 'core'
    
    def __unicode__(self):
        return self.name
        
    @property
    def system(self):
        return self.uuid == settings.ETHICS_COMMISSION_UUID

class ExpeditedReviewCategory(models.Model):
    name = models.CharField(max_length=60)
    abbrev = models.CharField(max_length=12)
    users = models.ManyToManyField(User, related_name='expedited_review_categories')

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.abbrev)

class MedicalCategory(models.Model):
    name = models.CharField(max_length=60)
    abbrev = models.CharField(max_length=12, unique=True)
    users = models.ManyToManyField(User, related_name='medical_categories')

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.abbrev)

