# -*- coding: utf-8 -*-
from django.db import models

STUDY_PRICING_OTHER = 1
STUDY_PRICING_MULTICENTRIC_AMG_MAIN = 2
STUDY_PRICING_MULTICENTRIC_AMG_LOCAL = 3
STUDY_PRICING_REMISSION = 4
EXTERNAL_REVIEW_PRICING = 5

PRICE_CATEGORIES = (
    (STUDY_PRICING_OTHER, u'Alle Studien außer multizentrische Arzneimittelstudien'),
    (STUDY_PRICING_MULTICENTRIC_AMG_MAIN, u'Multizentrische Arzneimittelstudien für Leit-Ethikkommissionen'),
    (STUDY_PRICING_MULTICENTRIC_AMG_LOCAL, u'Multizentrische Arzneimittelstudien für lokal zuständige Ethikkommissionen'),
    (STUDY_PRICING_REMISSION, u'Gebührenbefreiung'),
    (EXTERNAL_REVIEW_PRICING, u'External Reviewer'),
)

class PriceManager(models.Manager):
    def for_submissions(self):
        return self.exclude(category=EXTERNAL_REVIEW_PRICING)

    def get_for_submission(self, submission, review=False):
        if submission.remission:
            return self.get(category=STUDY_PRICING_REMISSION)
        if submission.is_amg and submission.multicentric:
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
    text = models.TextField(blank=True)
    
    objects = PriceManager()
    
    def __unicode__(self):
        return dict(PRICE_CATEGORIES)[self.category]
