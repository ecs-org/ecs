# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module

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

class Checklist(models.Model):
    class Meta:
        app_label = 'core'

class VoteReview(models.Model):
    class Meta:
        app_label = 'core'

class Vote(models.Model):
    votereview = models.ForeignKey(VoteReview)
    submissionform = models.ForeignKey('core.SubmissionForm', null=True)
    checklists = models.ManyToManyField(Checklist)
    
    class Meta:
        app_label = 'core'

class SubmissionReview(models.Model):
    class Meta:
        app_label = 'core'


class NotificationAnswer(models.Model):
    class Meta:
        app_label = 'core'

# Register models conditionally to avoid `already registered` errors when this module gets loaded twice.
if not reversion.is_registered(Amendment):
    reversion.register(Amendment) 
    reversion.register(Checklist) 
    reversion.register(EthicsCommission) 
    reversion.register(SubmissionReview) 
    reversion.register(NotificationAnswer) 
    reversion.register(Vote) 
    reversion.register(VoteReview) 
