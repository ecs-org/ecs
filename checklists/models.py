# -*- coding: utf-8 -*-
from datetime import datetime
from uuid import uuid4

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from ecs.authorization import AuthorizationManager
from ecs.documents.models import Document
from ecs.utils.viewutils import render_pdf_context
from ecs.documents.models import DocumentType

class ChecklistBlueprint(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=50, db_index=True, unique=True)
    multiple = models.BooleanField(default=False)
    billing_required = models.BooleanField(default=False)
    reviewer_is_anonymous = models.BooleanField(default=False)

    def __unicode__(self):
        return _(self.name)

class ChecklistQuestion(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='questions')
    number = models.CharField(max_length=5, db_index=True)
    index = models.IntegerField(db_index=True)
    text = models.CharField(max_length=200)
    description = models.CharField(max_length=500, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    is_inverted = models.BooleanField(default=False)
    requires_comment = models.BooleanField(default=False)

    class Meta:
        unique_together = (('blueprint', 'number'),)
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
    pdf_document = models.OneToOneField(Document, related_name="checklist", null=True)

    objects = AuthorizationManager()
    
    @property
    def short_name(self):
        if self.blueprint.multiple:
            return "%s (%s)" % (self.blueprint, self.user)
        return unicode(self.blueprint)

    def __unicode__(self):
        if not self.submission:
            return self.short_name
        return u'%s für %s' % (self.short_name, unicode(self.submission))
        
    @property
    def is_complete(self):
        return not self.answers.filter(answer=None).exists()

    @property
    def is_positive(self):
        return self.answers.filter(Q(question__is_inverted=False, answer=False) | Q(question__is_inverted=True, answer=True)).count() == 0

    @property
    def is_negative(self):
        return not self.is_positive

    def get_answers_with_comments(self, answer=None):
        if answer is None:
            q = Q(answer=None)
        else:
            q = Q(question__is_inverted=False, answer=answer) | Q(question__is_inverted=True, answer=not answer)
        return self.answers.exclude(comment=None).exclude(comment="").filter(q).order_by('question')

    def get_all_answers_with_comments(self):
        return self.answers.exclude(comment=None).exclude(comment="").order_by('question')

    @property
    def has_positive_comments(self):
        return self.get_answers_with_comments(True).exists()

    @property
    def has_negative_comments(self):
        return self.get_answers_with_comments(False).exists()

    def render_pdf(self):
        doctype = DocumentType.objects.get(identifier='checklist')
        if self.blueprint.reviewer_is_anonymous:
            if self.submission:
                name = u'{0} für {1}'.format(self.blueprint, self.submission)
            else:
                name = unicode(self.blueprint)
            name = '{0}-{1}'.format(name, uuid4().get_hex()[:5])
        else:
            name = unicode(self)
        filename = u'{0}.pdf'.format(slugify(name))

        pdfdata = render_pdf_context('db/checklists/wkhtml2pdf/checklist.html', {
            'checklist': self,
        })

        self.pdf_document = Document.objects.create_from_buffer(pdfdata, doctype=doctype,
            parent_object=self, name=name, original_file_name=filename, version='1',
            date=datetime.now())
        self.save()

    def get_submission(self):
        return self.submission


class ChecklistAnswer(models.Model):
    checklist = models.ForeignKey(Checklist, related_name='answers')
    question = models.ForeignKey(ChecklistQuestion)
    answer = models.NullBooleanField(null=True)
    comment = models.TextField(null=True, blank=True)

    objects = AuthorizationManager()

    class Meta:
        ordering = ('question__blueprint', 'question__index')

    def __unicode__(self):
        return u"Answer to '%s': %s" % (self.question, self.answer)

    @property
    def is_answered(self):
        return self.answer is not None

    @property
    def is_positive(self):
        return (not self.question.is_inverted and self.answer) or (self.question.is_inverted and self.answer == False)

    @property
    def is_negative(self):
        return not self.is_positive
