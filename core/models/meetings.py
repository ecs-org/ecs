# -*- coding: utf-8 -*-
from datetime import timedelta
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.contrib.auth.models import User

from ecs.utils import cached_property

import reversion

#impediments = p.get_impediments(time, event.duration)
#if impediments:
#    self.impediments.setdefault(p, []).extend(impediments)
#if p not in self.impediments:
#    self.impediments[p] =


class TimetableMetrics(object):
    def __init__(self, permutation, entries_by_user=None, users_by_entry=None):
        self.entries_by_user = {}
        self.users_by_entry = {}
        for p in Participation.objects.filter(entry__in=permutation).select_related('entry', 'user'):
            self.entries_by_user.setdefault(p.user, set()).add(p.entry)
            self.users_by_entry.setdefault(p.entry, set()).add(p.user)
        self.waiting_time_per_user = {}
        for user in self.entries_by_user:
            self.waiting_time_per_user[user] = timedelta(seconds=0)
        #self.impediments = {}
        offset = timedelta(seconds=0)
        participants = set()
        visited_entries = set()
        for entry in permutation:
            entry_participants = self.users_by_entry[entry]
            for user in participants.difference(entry_participants):
                self.waiting_time_per_user[user] += entry.duration
            visited_entries.add(entry)
            for user in entry_participants:
                 if self.entries_by_user[user] <= visited_entries:
                     if user in participants:
                         participants.remove(user)
                 else:
                     participants.add(user)
            offset += entry.duration

    @cached_property
    def total_waiting_time(self):
        s = timedelta(seconds=0)
        for time in self.waiting_time_per_user.itervalues():
            s += time
        return s
        
    @cached_property
    def avg_waiting_time(self):
        if not self.entries_by_user:
            return timedelta(seconds=0)
        return self.total_waiting_time / len(self.entries_by_user)
        
    @cached_property
    def max_waiting_time(self):
        if not self.waiting_time_per_user:
            return timedelta(seconds=0)
        return max(self.waiting_time_per_user.itervalues())

    @cached_property
    def min_waiting_time(self):
        if not self.waiting_time_per_user:
            return timedelta(seconds=0)
        return min(self.waiting_time_per_user.itervalues())


class Meeting(models.Model):
    start = models.DateTimeField()
    title = models.CharField(max_length=200, blank=True)
    
    class Meta:
        app_label = 'core'
        
    @cached_property
    def duration(self):
        return timedelta(seconds=self.timetable_entries.aggregate(sum=models.Sum('duration_in_seconds'))['sum'])

    @property
    def end(self):
        return self.start + self.duration
        
    @cached_property
    def metrics(self):
        return TimetableMetrics(self)
        
    @property
    def users(self):
        return User.objects.filter(meeting_participations__entry__meeting=self).distinct().order_by('username')
        
    @property
    def users_with_constraints(self):
        constraints_by_user_id = {}
        for constraint in self.constraints.order_by('start_time'):
            constraints_by_user_id.setdefault(constraint.user_id, []).append(constraint)
        for user in self.users:
            user.constraints = constraints_by_user_id.get(user.id, [])
            yield user
        
    def _clear_caches(self):
        del self.metrics
        del self.duration
        
    def add_entry(self, **kwargs):
        last_index = self.timetable_entries.aggregate(models.Max('timetable_index'))['timetable_index__max']
        if last_index is None:
            kwargs['timetable_index'] = 0
        else:
            kwargs['timetable_index'] = last_index + 1
        duration = kwargs.pop('duration', None)
        if duration:
            kwargs['duration_in_seconds'] = duration.seconds
        entry = self.timetable_entries.create(**kwargs)
        self._clear_caches()
        return entry

    def add_break(self, **kwargs):
        kwargs['is_break'] = True
        entry = self.add_entry(**kwargs)
        self._clear_caches()
        return entry
        
    def __getitem__(self, index):
        if not isinstance(index, int):
            raise KeyError()
        if index < 0:
            raise IndexError()
        try:
            return self.timetable_entries.get(timetable_index=index)
        except TimetableEntry.DoesNotExist:
            raise IndexError()
            
    def __delitem__(self, index):
        self[index].delete()
        self._clear_caches()
        
    def __len__(self):
        return self.timetable_entries.count()
        
    def __iter__(self):
        duration = timedelta(seconds=0)
        users_by_entry_id = {}
        for participation in Participation.objects.filter(entry__meeting=self).select_related('user').order_by('user__username'):
            users_by_entry_id.setdefault(participation.entry_id, []).append(participation.user)
        for entry in self.timetable_entries.order_by('timetable_index'):
            entry.users = users_by_entry_id.get(entry.id, [])
            entry.start = self.start + duration
            duration += entry.duration
            entry.end = self.start + duration
            yield entry
        self._duration = duration
        
    def _get_start_for_index(self, index):
        offset = self.timetable_entries.filter(timetable_index__lt=index).aggregate(sum=models.Sum('duration_in_seconds'))['sum']
        return self.start + timedelta(seconds=offset or 0)
    

class TimetableEntry(models.Model):
    meeting = models.ForeignKey(Meeting, related_name='timetable_entries')
    title = models.CharField(max_length=200, blank=True)
    timetable_index = models.IntegerField()
    duration_in_seconds = models.PositiveIntegerField()
    is_break = models.BooleanField(default=False)
    submission = models.ForeignKey('core.Submission', null=True)
    
    class Meta:
        app_label = 'core'
        #unique_together = (('meeting', 'timetable_index'),)
        
    def __unicode__(self):
        return "%s, index=%s" % (self.title, self.timetable_index)
    
    @property
    def duration(self):
        return timedelta(seconds=self.duration_in_seconds)
        
    @cached_property
    def users(self):
        return User.objects.filter(meeting_participations__entry=self).order_by('username')
    
    def _get_index(self):
        return self.timetable_index
        
    #@transaction.???
    def _set_index(self, index):
        if index < 0 or index >= len(self.meeting):
            raise IndexError()
        old_index = self.timetable_index
        if index == old_index:
            return
        if old_index > index:
            self.meeting.timetable_entries.filter(timetable_index__gte=index, timetable_index__lt=old_index).update(timetable_index=models.F('timetable_index') + 1)
        elif old_index < index:
            self.meeting.timetable_entries.filter(timetable_index__gt=old_index, timetable_index__lte=index).update(timetable_index=models.F('timetable_index') - 1)
        self.timetable_index = index
        self.save(force_update=True)
    
    index = property(_get_index, _set_index)
    
    @cached_property
    def start(self):
        return self.meeting._get_start_for_index(self.timetable_index)
        
    @cached_property
    def end(self):
        return self.start + self.duration

def _timetable_entry_delete_post_delete(sender, **kwargs):
    entry = kwargs['instance']
    entry.meeting.timetable_entries.filter(timetable_index__gt=entry.index).update(timetable_index=models.F('timetable_index') - 1)

post_delete.connect(_timetable_entry_delete_post_delete, sender=TimetableEntry)

class Participation(models.Model):
    entry = models.ForeignKey(TimetableEntry, related_name='participations')
    user = models.ForeignKey(User, related_name='meeting_participations')
    
    class Meta:
        app_label = 'core'

class Constraint(models.Model):
    meeting = models.ForeignKey(Meeting, related_name='constraints')
    user = models.ForeignKey(User, related_name='meeting_constraints')
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    weight = models.FloatField(default=0.5)

    class Meta:
        app_label = 'core'


# Register models conditionally to avoid `already registered` errors when this module gets loaded twice.
#if not reversion.is_registered(Meeting):
#    reversion.register(Meeting) 
#    reversion.register(TimeTableEntry)
