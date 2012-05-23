from functools import wraps
import time

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from ecs.meetings.models import Meeting


def cache_key_for_meeting_page(meeting, fn):
    return 'meeting:{0}:{1}'.format(meeting.pk, fn.func_name)

def cache_meeting_page(timeout=60*10, render_timeout=5):
    def _decorator(fn):
        @wraps(fn)
        def _inner(*args, **kwargs):
            meeting_pk = kwargs.pop('meeting_pk')
            # getting the meeting from the database is an implicit permission check
            meeting = get_object_or_404(Meeting, pk=meeting_pk)
            kwargs['meeting'] = meeting
            cache_key = cache_key_for_meeting_page(meeting, fn)
            lock_key = cache_key + ':render-lock'
            while True:
                html = cache.get(cache_key)
                if html is None:
                    if cache.add(lock_key, 'in-progress', render_timeout):
                        break
                    else:
                        time.sleep(1)
                else:
                    return HttpResponse(html)
            try:
                html = fn(*args, **kwargs)
                cache.set(cache_key, html, timeout)
                return HttpResponse(html)
            finally:
                cache.delete(lock_key)
        return _inner
    return _decorator

def flush_meeting_page_cache(meeting, fn):
    cache_key = cache_key_for_meeting_page(meeting, fn)
    cache.delete(cache_key)
