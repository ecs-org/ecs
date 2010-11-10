# -*- coding: utf-8 -*-

from django.db import models


class FastLaneMeeting(models.Model):
    start = models.DateTimeField()
    title = models.CharField(max_length=150)
    started = models.DateTimeField(null=True)
    ended = models.DateTimeField(null=True)
    submissions = models.ManyToManyField('core.Submission', through='FastLaneTop', related_name='fast_lane_meetings')


class FastLaneTop(models.Model):
    submission = models.ForeignKey('core.Submission', related_name='fast_lane_tops', unique=True)
    meeting = models.ForeignKey('fastlane.FastLaneMeeting', related_name='tops')
    recommendation = models.NullBooleanField(blank=True, default=None)
    recommendation_comment = models.TextField(blank=True)

class AssignedFastLaneCategory(models.Model):
    tops = models.ManyToManyField('fastlane.FastLaneTop')
    user = models.ForeignKey('auth.User', related_name='assigned_fastlane_categories', null=True, blank=True)
    category = models.ForeignKey('core.ExpeditedReviewCategory', related_name='assigned_fastlane_categories', unique=True)


