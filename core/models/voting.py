# -*- coding: utf-8 -*-
from django.db import models

VOTE_RESULT_CHOICES = (
    ('1a', u'1a Positiv'),
    ('1b', u'1b Positiv - mit Ausbesserungen'),
    ('2', u'2 Vertagt wegen Einsprüchen'),
    ('3', u'3 Negativ'),
    ('4', u'4 Vertagt'),
)

class Vote(models.Model):
    top = models.OneToOneField('core.TimetableEntry', related_name='vote')
    result = models.CharField(max_length=2, choices=VOTE_RESULT_CHOICES)
    executive_review_required = models.BooleanField()
    text = models.TextField(blank=True)
    
    class Meta:
        app_label = 'core'