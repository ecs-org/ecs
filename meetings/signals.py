from django.dispatch import Signal

on_meeting_end = Signal() # sender: Meeting, kwargs: meeting
