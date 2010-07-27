# -*- coding: utf-8 -*-
from copy import deepcopy
from django.utils.datastructures import SortedDict
from ecs.billing.models import Price, STUDY_PRICING_OTHER, STUDY_PRICING_MULTICENTRIC_AMG_MAIN, STUDY_PRICING_MULTICENTRIC_AMG_LOCAL, STUDY_PRICING_REMISSION

SUBMISSION_STAT_TEMPLATE = SortedDict((
    ('local', {
        'label': u'Gebührennoten - lokale EK',
        'price': STUDY_PRICING_MULTICENTRIC_AMG_LOCAL,
        'count': 0,
    }),
    ('amg', {
        'label': u'Gebührennoten - AMG',
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
    ('mpg', {
        'label': u'Gebührennoten - MPG',
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
    ('other', {
        'label': u'Gebührennoten - sonstige',
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
    ('main_monocentric', {
        'label': u'Gebührennoten - Leit-EK monozentrisch',
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
    ('main_multicentric', {
        'label': u'Gebührennoten - Leit-EK multizentrisch',
        'price': STUDY_PRICING_MULTICENTRIC_AMG_MAIN,
        'count': 0,
    }),
    # FIXME: what does 
    ('later', {
        'label': u'Gebührennotennachreichungen',
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
))

AMG_KEYS = {
    # (multicentric, main)
    (True, True): 'main_multicentric',
    (False, True): 'main_monocentric',
    (False, False): 'amg',
    (True, False): 'local',
}

def collect_submission_billing_stats(submission_list):
    summary = deepcopy(SUBMISSION_STAT_TEMPLATE)
    total = 0
    for submission in submission_list:
        if submission.is_amg:
            key = AMG_KEYS[(submission.multicentric, getattr(submission.main_ethics_commission, 'system', False))]
        elif submission.is_mpg:
            key = 'mpg'
        else:
            key = 'other'
        summary[key]['count'] += 1
        total += submission.price.price

    for val in summary.values():
        val['price'] = Price.objects.get(category=val['price'])

    return summary, total