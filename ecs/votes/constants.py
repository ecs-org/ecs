from django.utils.translation import ugettext_lazy as _

VOTE_PREPARATION_CHOICES = (
    ('1', _('1 positive')),
    ('2', _('2 positive under reserve')),
)

B3b = ('3b', _('3b recessed (examined)'))

B2_VOTE_PREPARATION_CHOICES = VOTE_PREPARATION_CHOICES + (B3b,)

VOTE_RESULT_CHOICES = VOTE_PREPARATION_CHOICES + (
    ('3a', _('3a recessed (not examined)')),
    B3b,
    ('4', _('4 negative')),
    ('5', _('5 withdrawn (applicant)')),
)

POSITIVE_VOTE_RESULTS = ('1', '2')
NEGATIVE_VOTE_RESULTS = ('4', '5')
RECESSED_VOTE_RESULTS = ('3a', '3b')

PERMANENT_VOTE_RESULTS = ('1',) + NEGATIVE_VOTE_RESULTS
