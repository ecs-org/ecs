# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

import reversion

class Workflow(models.Model):
    class Meta:
        app_label = 'core'

class EthicsCommission(models.Model):
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


# FIXME: Amendment is unused
class Amendment(models.Model):
    # FIXME: rename to `submission_form`
    submissionform = models.ForeignKey('core.SubmissionForm')
    order = models.IntegerField()
    number = models.CharField(max_length=40)
    date = models.DateField()
    
    class Meta:
        app_label = 'core'


class VoteReview(models.Model):
    class Meta:
        app_label = 'core'

class Vote(models.Model):
    votereview = models.ForeignKey(VoteReview)
    submissionform = models.ForeignKey('core.SubmissionForm', null=True)

    class Meta:
        app_label = 'core'

class SubmissionReview(models.Model):
    class Meta:
        app_label = 'core'


class NotificationAnswer(models.Model):
    class Meta:
        app_label = 'core'


class ExpeditedReviewCategory(models.Model):
    name = models.CharField(max_length=60)
    abbrev = models.CharField(max_length=12)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.abbrev)


class MedicalCategory(models.Model):
    name = models.CharField(max_length=60)
    abbrev = models.CharField(max_length=12)
    users = models.ManyToManyField(User, related_name='medical_categories')

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.abbrev)


# Register models conditionally to avoid `already registered` errors when this module gets loaded twice.
if not reversion.is_registered(Amendment):
    reversion.register(Amendment) 
    reversion.register(EthicsCommission) 
    reversion.register(SubmissionReview) 
    reversion.register(NotificationAnswer) 
    reversion.register(Vote) 
    reversion.register(VoteReview) 
    reversion.register(MedicalCategory)
    reversion.register(ExpeditedReviewCategory)
