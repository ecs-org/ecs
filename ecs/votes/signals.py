from django.dispatch import Signal

on_vote_publication = Signal() # sender=Vote, kwargs: vote
