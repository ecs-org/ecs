# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey

from ecs.core.models.submissions import Submission


class ChecklistBlueprint(models.Model):
    name = models.CharField(max_length=100)
    min_document_count = models.PositiveIntegerField(null=True, choices=((None, 'none'), (0, 'optional documents'), (1, 'one mandatory document')))

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return self.name

class ChecklistQuestion(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='questions')
    text = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return u"%s: '%s'" % (self.blueprint, self.text)

class Checklist(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='checklists')
    submission = models.ForeignKey('core.Submission', related_name='checklists', null=True)
    #object = GenericForeignKey()  # Postponed
    user = models.ForeignKey('auth.user')
    documents = models.ManyToManyField('documents.Document')

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return u"%s" % self.blueprint
        
    @property
    def is_complete(self):
        if self.answers.filter(answer=None).count() == 0:
            mindocs = self.blueprint.min_document_count
            print mindocs, self.documents.count()
            if mindocs is None or self.documents.count() >= mindocs:
                return True
        return False
        
    @property
    def is_positive(self):
        return self.answers.filter(answer=False).count() == 0
        
    @property
    def is_negative(self):
        return not self.is_positive
        
    def get_answers_with_comments(self, answer=None):
        return self.answers.exclude(comment=None).exclude(comment="").filter(answer=answer).order_by('question')
        
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

    def __unicode__(self):
        return u"Answer to '%s': %s" % (self.question, self.answer)

