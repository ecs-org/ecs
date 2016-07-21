from copy import deepcopy
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from ecs.core.models import Submission
from ecs.votes.models import Vote


class _Entry(object):
    def __init__(self, slug, label, paper_number, with_listing=False):
        self.slug = slug
        self.label = label
        self.paper_number = paper_number
        self.submissions = []
        self.with_listing = with_listing

    def add_submission(self, submission):
        self.submissions.append(submission)

    @property
    def count(self):
        return len(self.submissions)


class _Section(object):
    def __init__(self, label, *entries):
        self.label = label
        self.entries = OrderedDict((entry.slug, entry) for entry in entries)

    def __iter__(self):
        return iter(self.entries.values())

    def __getitem__(self, key):
        return self.entries[key]


STATS_TEMPLATE = OrderedDict((
    ('submissions', _Section(_('Submissions'),
        _Entry('total', _('Total'), '2.0'),
        _Entry('no_remission', _('Comercially sponsored'), '2.1'),
        _Entry('multicentric', _('Multicentric'), '2.2'),
        _Entry('amg', _('In accord with AMG'), '2.4'),
        _Entry('mpg', _('In accord with MPG'), '2.5'),
        _Entry('b1_on_first_vote', _('B1 on first vote'), '2.6'),
        _Entry('b2_on_first_vote', _('B2 on first vote'), '2.7'),
        _Entry('recessed_on_first_vote', _('B3 on first vote'), '2.8'),
        _Entry('negative', _('Negative overall'), '2.9'),
    )),
    ('amg', _Section(_('In accord with AMG'),
        _Entry('multicentric_main', _('Main Ethics Commission'), '3.1'),
        _Entry('multicentric_local', _('Local Ethics Commission'), '3.2'),
        _Entry('monocentric', _('Monocentric AMG studies'), '3.4'),
    )),
    ('mpg', _Section(_('In accord with MPG'),
        _Entry('ce_certified_for_exact_indications',
            _('CE certified for exact indications'), '4.1', with_listing=True),
        _Entry('ce_certified_for_other_indications',
            _('CE certified for other indications'), '4.2', with_listing=True),
        _Entry('no_ce', _('Without CE marking'), '4.3', with_listing=True),
        _Entry('also_amg', _('Studies in accord with AMG and MPG'), '4.4', with_listing=True),
    )),
))


def collect_submission_stats_for_year(year):
    submission_stats = deepcopy(STATS_TEMPLATE)

    votes = Vote.objects.exclude(published_at=None)
    submissions = (Submission.objects
        .for_year(year)
        .filter(id__in=votes.values('submission_form__submission__id').query)
        .order_by('ec_number').select_related('current_submission_form'))

    for s in submissions:
        sf = s.current_submission_form
        first_vote = s.votes.exclude(published_at=None).order_by('published_at')[0]
        has_foreign_centers = sf.foreignparticipatingcenter_set.exists()

        classification = {
            'submissions.total': True,
            'submissions.no_remission': not s.remission,
            'submissions.multicentric': sf.is_multicentric or has_foreign_centers,
            'submissions.amg': sf.is_amg,
            'submissions.mpg': sf.is_mpg,
            'submissions.b1_on_first_vote': first_vote.result == '1',
            'submissions.b2_on_first_vote': first_vote.result == '2',
            'submissions.recessed_on_first_vote': first_vote.is_recessed,
            'submissions.negative': s.current_published_vote.is_negative,
            'amg.multicentric_main':
                sf.is_amg and sf.is_categorized_multicentric_and_main or
                (sf.is_categorized_monocentric and has_foreign_centers),
            'amg.multicentric_local':
                sf.is_amg and sf.is_categorized_multicentric_and_local,
            'amg.monocentric': sf.is_amg and
                sf.is_categorized_monocentric and not has_foreign_centers,
            'mpg.ce_certified_for_exact_indications': sf.is_mpg and
                sf.medtech_ce_symbol and sf.medtech_certified_for_exact_indications,
            'mpg.ce_certified_for_other_indications': sf.is_mpg and
                sf.medtech_ce_symbol and sf.medtech_certified_for_other_indications,
            'mpg.no_ce': sf.is_mpg and not sf.medtech_ce_symbol,
            'mpg.also_amg': sf.is_amg and sf.is_mpg,
        }

        for key, value in classification.items():
            section, entry = key.split('.', 1)
            if value:
                submission_stats[section][entry].add_submission(s)

    return submission_stats
