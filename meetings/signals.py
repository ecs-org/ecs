from django.dispatch import Signal

on_meeting_start = Signal()             # sender: Meeting, kwargs: meeting
on_meeting_end = Signal()               # sender: Meeting, kwargs: meeting
on_meeting_date_changed = Signal()      # sender: Meeting, kwargs: meeting
on_meeting_top_close = Signal()         # sender: Meeting, kwargs: meeting, timetable_entry
on_meeting_top_add = Signal()           # sender: Meeting, kwargs: meeting, timetable_entry
on_meeting_top_delete = Signal()        # sender: Meeting, kwargs: meeting, timetable_entry
on_meeting_top_index_change = Signal()  # sender: Meeting, kwargs: meeting, timetable_entry
