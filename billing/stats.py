# -*- coding: utf-8 -*-
from copy import deepcopy
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from ecs.billing.models import Price, STUDY_PRICING_OTHER, STUDY_PRICING_MULTICENTRIC_AMG_MAIN, STUDY_PRICING_MULTICENTRIC_AMG_LOCAL

SUBMISSION_STAT_TEMPLATE = SortedDict((
    ('local', {
        'label': _(u'fees note - local EC'),
        'price': STUDY_PRICING_MULTICENTRIC_AMG_LOCAL,
        'count': 0,
    }),
    ('amg', {
        'label': _(u'fees note - AMG'),
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
    ('mpg', {
        'label': _(u'fees note - MPG'),
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
    ('other', {
        'label': _(u'fees note - other'),
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
    ('main_monocentric', {
        'label': _(u'fees note - controlling-EC monocentric'),
        'price': STUDY_PRICING_OTHER,
        'count': 0,
    }),
    ('main_multicentric', {
        'label': _(u'fees note - controlling-EC multicentric'),
        'price': STUDY_PRICING_MULTICENTRIC_AMG_MAIN,
        'count': 0,
    }),
    # FIXME: what does 
    ('later', {
        'label': _(u'late filed fees notes'),
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
        if submission.current_submission_form.is_amg:
            key = AMG_KEYS[(submission.is_multicentric, getattr(submission.main_ethics_commission, 'system', False))]
        elif submission.current_submission_form.is_mpg:
            key = 'mpg'
        else:
            key = 'other'
        summary[key]['count'] += 1
        total += submission.price.price

    for val in summary.values():
        val['price'] = Price.objects.get(category=val['price'])

    return summary, total
