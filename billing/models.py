# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode as fu
from django.contrib.auth.models import User

from ecs.authorization import AuthorizationManager

STUDY_PRICING_OTHER = 1
STUDY_PRICING_MULTICENTRIC_AMG_MAIN = 2
STUDY_PRICING_MULTICENTRIC_AMG_LOCAL = 3
STUDY_PRICING_REMISSION = 4
EXTERNAL_REVIEW_PRICING = 5

PRICE_CATEGORIES = (
    (STUDY_PRICING_OTHER, _(u'All studies except multicentre drug studies')),
    (STUDY_PRICING_MULTICENTRIC_AMG_MAIN, _(u'Multicentre drug trials for controlling ethics committees')),
    (STUDY_PRICING_MULTICENTRIC_AMG_LOCAL, _(u'Multicentre drug trials for locally responsible ethics committees')),
    (STUDY_PRICING_REMISSION, _(u'fee exemption')),
    (EXTERNAL_REVIEW_PRICING, _(u'External Reviewer')),
)

class PriceManager(models.Manager):
    def for_submissions(self):
        return self.exclude(category=EXTERNAL_REVIEW_PRICING)

    def get_for_submission(self, submission, review=False):
        if submission.remission:
            return self.get(category=STUDY_PRICING_REMISSION)
        if submission.current_submission_form.is_amg and submission.is_multicentric:
            main_ec = submission.main_ethics_commission
            if main_ec and main_ec.system:
                return self.get(category=STUDY_PRICING_MULTICENTRIC_AMG_MAIN)
            else:
                return self.get(category=STUDY_PRICING_MULTICENTRIC_AMG_LOCAL)
        return self.get(category=STUDY_PRICING_OTHER)
        
    def get_review_price(self):
        return self.get(category=EXTERNAL_REVIEW_PRICING)
        


class Price(models.Model):
    category = models.SmallIntegerField(choices=PRICE_CATEGORIES, unique=True, db_index=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    objects = PriceManager()

    @property
    def text(self):
        return dict(PRICE_CATEGORIES)[self.category]
    
    def __unicode__(self):
        return dict(PRICE_CATEGORIES)[self.category]

class ChecklistBillingState(models.Model):
    checklist = models.OneToOneField('checklists.Checklist', null=True, related_name='billing_state')
    billed_at = models.DateTimeField(null=True, default=None, blank=True, db_index=True)

    objects = AuthorizationManager()

class Invoice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    submissions = models.ManyToManyField('core.Submission')
    document = models.OneToOneField('documents.Document', related_name="invoice", null=True)

    @property
    def stats(self):
        from ecs.billing.stats import collect_submission_billing_stats
        return collect_submission_billing_stats(self.submissions.all())

class ChecklistPayment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    checklists = models.ManyToManyField('checklists.Checklist')
    document = models.OneToOneField('documents.Document', related_name="checklist_payment", null=True)

    @property
    def reviewers(self):
        return User.objects.filter(pk__in=[c.user.pk for c in self.checklists.all()]).distinct()

    @property
    def stats(self):
        from ecs.billing.stats import collect_checklist_billing_stats
        return collect_checklist_billing_stats(self.checklists.all())
