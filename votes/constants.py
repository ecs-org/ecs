from django.utils.translation import ugettext_lazy as _

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
