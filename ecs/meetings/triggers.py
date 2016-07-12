from ecs.meetings import signals
from ecs.utils import connect
from ecs.votes.models import Vote
from ecs.meetings.cache import flush_meeting_page_cache


def _flush_cache(meeting):
    from ecs.meetings.views import submission_list, tops
    flush_meeting_page_cache(meeting, submission_list)
    flush_meeting_page_cache(meeting, tops)

@connect(signals.on_meeting_start)
def on_meeting_start(sender, **kwargs):
    meeting = kwargs['meeting']
    _flush_cache(meeting)

@connect(signals.on_meeting_end)
def on_meeting_end(sender, **kwargs):
    meeting = kwargs['meeting']

    for vote in Vote.objects.filter(top__meeting=meeting):
        vote.save() # trigger post_save for all votes

    for top in meeting.additional_entries.exclude(pk__in=Vote.objects.exclude(top=None).values('top__pk').query):
        vote = Vote.objects.create(top=top, result='3a',
            submission_form=top.submission.current_submission_form)
        top.is_open = False
        top.save()

    _flush_cache(meeting)

@connect(signals.on_meeting_date_changed)
def on_meeting_date_changed(sender, **kwargs):
    meeting = kwargs['meeting']
    _flush_cache(meeting)

@connect(signals.on_meeting_top_jump)
def on_meeting_top_jump(sender, **kwargs):
    meeting = kwargs['meeting']
    timetable_entry = kwargs['timetable_entry']
    _flush_cache(meeting)

@connect(signals.on_meeting_top_add)
def on_meeting_top_add(sender, **kwargs):
    meeting = kwargs['meeting']
    timetable_entry = kwargs['timetable_entry']
    _flush_cache(meeting)

@connect(signals.on_meeting_top_delete)
def on_meeting_top_delete(sender, **kwargs):
    meeting = kwargs['meeting']
    timetable_entry = kwargs['timetable_entry']
    _flush_cache(meeting)

@connect(signals.on_meeting_top_index_change)
def on_meeting_top_index_change(sender, **kwargs):
    meeting = kwargs['meeting']
    timetable_entry = kwargs['timetable_entry']
    _flush_cache(meeting)
