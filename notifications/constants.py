# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

SAFETY_TYPE_CHOICES = (
    ('susar', _(u'SUSAR')),
    ('sae', _(u'SAE')),
    ('asr', _(u'Annual Safety Report')),
    ('other', _(u'Other Safety Report')),
)