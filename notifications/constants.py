# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

SAFETY_TYPE_CHOICES = (
    ('susar', _(u'SUSAR')),
    ('sae', _(u'SAE')),
    ('asr', _(u'Annual Safety Report')),
    ('other', _(u'Other Safety Report')),
)

NOTIFICATION_REVIEW_LANE_CHOICES = (
    ('exerev', 'Executive Review'),
    ('notrev', 'Notification Group Review'),
    ('insrev', 'Insurance Group Review'),
)