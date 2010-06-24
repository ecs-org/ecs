# -*- coding: utf-8 -*-
from django.db import models

VOTE_RESULT_CHOICES = (
    ('1', u'1 Positiv'),
    ('1a', u'1a Positiv - mit Ausbesserungen'),
    ('2', u'2 Vorbehaltich positiv'),
    ('3', u'3 Vertagt (Einwände)'),
    ('4', u'4 Negativ'),
    ('5', u'5 Vertagt (Antragsteller)'),
    ('5a', u'5a Zurückgezogen (Antragsteller)'),
    ('5b', u'5b Nicht behandelt'),
    #('5c', u'5c Lokale EK'),
)

class Vote(models.Model):
    top = models.OneToOneField('core.TimetableEntry', related_name='vote')
    result = models.CharField(max_length=2, choices=VOTE_RESULT_CHOICES, null=True, verbose_name=u'Votum')
    executive_review_required = models.NullBooleanField(blank=True)
    text = models.TextField(blank=True, verbose_name=u'Kommentar')
    
    class Meta:
        app_label = 'core'

    def __unicode__(self):
        if self.top:
            top = self.top
            if top.submission:
                submission = top.submission
                if submission.ec_number:
                    ec_number = submission.ec_number
                    return 'Votum %s' % ec_number
        return "Votum ID %s" % self.pk
        
    @property
    def positive(self):
        return self.result in ('1', '1a', '2')
        
    @property
    def negative(self):
        return self.result in ('4', '5a')
        
    @property
    def recessed(self):
        return self.result in ('3', '5', '5b')
        
    @property
    def activates(self):
        return self.result in ('1', '1a')
    
