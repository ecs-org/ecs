# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _

from ecs.authorization import AuthorizationManager

class ChecklistBlueprint(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=50, db_index=True, unique=True)
    multiple = models.BooleanField(default=False)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return _(self.name)

class ChecklistQuestion(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='questions')
    number = models.CharField(max_length=5)
    index = models.IntegerField()
    text = models.CharField(max_length=200)
    description = models.CharField(max_length=400, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    inverted = models.BooleanField(default=False)

    class Meta:
        app_label = 'core'
        unique_together = (('blueprint', 'number'), ('blueprint', 'index'))
        ordering = ('blueprint', 'index',)

    def __unicode__(self):
        return u"%s: '%s'" % (self.blueprint, self.text)


CHECKLIST_STATUS_CHOICES = (
    ('new', _('New')),
    ('completed', _('Completed')),
    ('review_ok', _('Review OK')),
    ('review_fail', _('Review Failed')),
    ('dropped', _('Dropped')),
)

class Checklist(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='checklists')
    submission = models.ForeignKey('core.Submission', related_name='checklists', null=True)
    user = models.ForeignKey('auth.user')
    status = models.CharField(max_length=15, default='new', choices=CHECKLIST_STATUS_CHOICES)

    objects = AuthorizationManager()

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        if self.blueprint.multiple:
            return "%s (%s)" % (self.blueprint, self.user)
        return u"%s" % self.blueprint

    @property
    def is_complete(self):
        return self.answers.filter(answer=None).count() == 0

    @property
    def is_positive(self):
        return self.answers.filter(Q(question__inverted=False, answer=False) | Q(question__inverted=True, answer=True)) == 0

    @property
    def is_negative(self):
        return not self.is_positive

    def get_answers_with_comments(self, answer=None):
        if answer is None:
            q = Q(answer=None)
        else:
            q = Q(question__inverted=False, answer=answer) | Q(question__inverted=True, answer=not answer)
        return self.answers.exclude(comment=None).exclude(comment="").filter(q).order_by('question')

    def get_all_answers_with_comments(self):
        return self.answers.exclude(comment=None).exclude(comment="").order_by('question')

    @property
    def has_positive_comments(self):
        return self.get_answers_with_comments(True).exists()

    @property
    def has_negative_comments(self):
        return self.get_answers_with_comments(False).exists()

class ChecklistAnswer(models.Model):
    checklist = models.ForeignKey(Checklist, related_name='answers')
    question = models.ForeignKey(ChecklistQuestion)
    answer = models.NullBooleanField(null=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ('question__blueprint', 'question__index')

    def __unicode__(self):
        return u"Answer to '%s': %s" % (self.question, self.answer)

    @property
    def is_answered(self):
        return self.answer is not None

    @property
    def is_positive(self):
        return (not self.question.inverted and self.answer) or (self.question.inverted and self.answer == False)

    @property
    def is_negative(self):
        return not self.is_positive
