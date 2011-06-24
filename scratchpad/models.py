# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.core.models.submissions import Submission

SCRATCHPAD_FORTUNES = (
    u'Wilkommen!',
    u'Alea iacta est.',
    u'Eat an apple on going to bed, and you’ll keep the doctor from earning his bread.',
    u'Auge um Auge lässt die Welt erblinden. (Gandhi)',
    u'Zwei Dinge sind unendlich: das All und die menschliche Dummheit. Bei letzterem bin ich mir noch nicht ganz sicher. (Einstein)',
    u'Ave Caesar, morituri te salutant',
    u'Zu Diensten!',
    u'Zu Risiken und Nebenwirkungen lesen Sie die Packungsbeilage und fragen Sie Ihren Arzt oder Apotheker.',
)


class ScratchPad(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    text = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User)
    submission = models.ForeignKey(Submission, null=True)

    class Meta:
        unique_together = (('owner', 'submission'),)

    def is_empty(self):
        return not self.text or self.text in SCRATCHPAD_FORTUNES
