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
    text = models.TextField()

    class Meta:
        app_label = 'core'


class Checklist(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='results')
    object = GenericForeignKey()  # to Submission, Notification, ..

    class Meta:
        app_label = 'core'


class ChecklistAnswer(models.Model):
    checklist = models.ForeignKey(Checklist)
    question = models.ForeignKey(ChecklistQuestion)
    answer = models.BooleanField(null=True)
    comment = models.TextField()

    class Meta:
        app_label = 'core'
