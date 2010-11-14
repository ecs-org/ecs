# -*- coding: utf-8 -*-

from django.db import models


class FastLaneMeeting(models.Model):
    start = models.DateTimeField()
    title = models.CharField(max_length=150)
    started = models.DateTimeField(null=True)
    ended = models.DateTimeField(null=True)
    submissions = models.ManyToManyField('core.Submission', through='FastLaneTop', related_name='fast_lane_meetings')

    def add_top(self, submission):
        top = FastLaneTop.objects.create(meeting=self, submission=submission)
        for category in submission.expedited_review_categories.all():
            AssignedFastLaneCategory.objects.get_or_create(category=category, meeting=self)
        return top


class FastLaneTop(models.Model):
    submission = models.OneToOneField('core.Submission', related_name='fast_lane_top', unique=True)
    meeting = models.ForeignKey('fastlane.FastLaneMeeting', related_name='tops')
    recommendation = models.NullBooleanField(blank=True, default=None)
    recommendation_comment = models.TextField(blank=True)

    @property
    def complete(self):
        return self.recommendation is not None

class AssignedFastLaneCategory(models.Model):
    meeting = models.ForeignKey('fastlane.FastLaneMeeting', related_name='categories', null=True)
    user = models.ForeignKey('auth.User', related_name='assigned_fastlane_categories', null=True, blank=True)
    category = models.ForeignKey('core.ExpeditedReviewCategory', related_name='assigned_fastlane_categories', unique=True)

    class Meta:
        unique_together = (('meeting', 'category'),)

    def get_submissions(self):
        return self.meeting.submissions.filter(expedited_review_categories=self.category)


