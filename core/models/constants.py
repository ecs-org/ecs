from django.utils.translation import ugettext_lazy as _

## submission
MIN_EC_NUMBER = 1000

SUBMISSION_TYPE_MONOCENTRIC = 1
SUBMISSION_TYPE_MULTICENTRIC = 2
SUBMISSION_TYPE_MULTICENTRIC_LOCAL = 6

SUBMISSION_TYPE_CHOICES = (
    (SUBMISSION_TYPE_MONOCENTRIC, _('monocentric')), 
    (SUBMISSION_TYPE_MULTICENTRIC, _('multicentric, main ethics commission')),
    (SUBMISSION_TYPE_MULTICENTRIC_LOCAL, _('multicentric, local ethics commission')),
)

SUBMISSION_INFORMATION_PRIVACY_CHOICES = (
    ('personal', _('individual-related')), 
    ('non-personal', _('implicit individual-related')),
)

## votes
VOTE_RESULT_CHOICES = (
    ('1', _(u'1 positive')),
    ('2', _(u'2 positive under reserve')),
    ('3a', _(u'3a recessed (not examined)')),
    ('3b', _(u'3b recessed (examined)')),
    ('4', _(u'4 negative')),
    ('5', _(u'5 withdrawn (applicant)')),
)

VOTE_RESULTS = [r for r, label in VOTE_RESULT_CHOICES]
POSITIVE_VOTE_RESULTS = ('1', '2')
NEGATIVE_VOTE_RESULTS = ('4', '5')
RECESSED_VOTE_RESULTS = ('3a', '3b')

FINAL_VOTE_RESULTS = POSITIVE_VOTE_RESULTS + NEGATIVE_VOTE_RESULTS

PERMANENT_POSITIVE_VOTE_RESULTS = ('1',)
PERMANENT_NEGATIVE_VOTE_RESULTS = NEGATIVE_VOTE_RESULTS
PERMANENT_VOTE_RESULTS = PERMANENT_POSITIVE_VOTE_RESULTS + NEGATIVE_VOTE_RESULTS


