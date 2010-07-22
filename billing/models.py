# -*- coding: utf-8 -*-
from django.db import models

STUDY_PRICING_OTHER = 1
STUDY_PRICING_MULTICENTRIC_DRUG_MAIN = 2
STUDY_PRICING_MULTICENTRIC_DRUG_LOCAL = 3
STUDY_PRICING_REMISSION = 4
EXTERNAL_REVIEW_PRICING = 5

PRICE_CATEGORIES = (
    (STUDY_PRICING_OTHER, u'Alle Studien außer multizentrische Arzneimittelstudien'),
    (STUDY_PRICING_MULTICENTRIC_DRUG_MAIN, u'Multizentrische Arzneimittelstudien für Leit-Ethikkommissionen'),
    (STUDY_PRICING_MULTICENTRIC_DRUG_LOCAL, u'Multizentrische Arzneimittelstudien für lokal zuständige Ethikkommissionen'),
    (STUDY_PRICING_REMISSION, u'External Reviewer'),
    (EXTERNAL_REVIEW_PRICING, u'Gebührenbefreiung'),
)

class PriceManager(models.Manager):
    def get_for_submission(self, submission):
        if submission.remission:
            return self.get(category=STUDY_PRICING_REMISSION)
        if submission.is_drug_study and submission.multicentric:
            if submission.main_ethics_commission.system:
                return self.get(category=STUDY_PRICING_MULTICENTRIC_DRUG_MAIN)
            else:
                return self.get(category=STUDY_PRICING_MULTICENTRIC_DRUG_LOCAL)
        return self.get(category=STUDY_PRICING_OTHER)

class Price(models.Model):
    category = models.SmallIntegerField(choices=PRICE_CATEGORIES, unique=True, db_index=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    text = models.TextField(blank=True)
    
    objects = PriceManager()
    
    def __unicode__(self):
        return dict(PRICE_CATEGORIES)[self.category]
