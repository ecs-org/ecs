from django.dispatch import Signal

on_vote_extension = Signal() # sender=Vote, kwargs: vote
on_vote_publication = Signal() # sender=Vote, kwargs: vote
on_vote_expiry = Signal() # sender=Submission, kwargs: submission
