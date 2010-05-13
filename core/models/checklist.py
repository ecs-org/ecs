# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey


class ChecklistBlueprint(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return self.name


class ChecklistQuestion(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='questions')
    text = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True)
    link = models.CharField(max_length=100, null=True)

    class Meta:
        app_label = 'core'


class Checklist(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='results')
    object = GenericForeignKey()  # to Submission, Notification, Vote ..

    class Meta:
        app_label = 'core'


class ChecklistAnswer(models.Model):
    checklist = models.ForeignKey(Checklist)
    question = models.ForeignKey(ChecklistQuestion)
    answer = models.NullBooleanField(null=True)
    comment = models.CharField(max_length=100)

    class Meta:
        app_label = 'core'
