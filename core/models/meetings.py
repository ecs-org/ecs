# -*- coding: utf-8 -*-
from datetime import timedelta
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.contrib.auth.models import User

import reversion

class Meeting(models.Model):
    start = models.DateTimeField()
    title = models.CharField(max_length=200, blank=True)
    
    class Meta:
        app_label = 'core'
        
    @property
    def duration(self):
        if not hasattr(self, '_duration'):
            self._duration = timedelta(seconds=self.timetable_entries.aggregate(sum=models.Sum('duration_in_seconds'))['sum'])
        return self._duration
    
    @property
    def end(self):
        return self.start + self.duration
        
    def _clear_caches(self):
        if hasattr(self, '_duration'):
            del self._duration
        
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
        except TimeTableEntry.DoesNotExist:
            raise IndexError()
            
    def __delitem__(self, index):
        self[index].delete()
        self._clear_caches()
        
    def __len__(self):
        return self.timetable_entries.count()
        
    def __iter__(self):
        duration = timedelta(seconds=0)
        for entry in self.timetable_entries.order_by('timetable_index'):
            entry._start = self.start + duration
            duration += entry.duration
            entry._end = self.start + duration
            yield entry
        self._duration = duration
        
    def _get_start_for_index(self, index):
        offset = self.timetable_entries.filter(timetable_index__lt=index).aggregate(sum=models.Sum('duration_in_seconds'))['sum']
        return self.start + timedelta(seconds=offset or 0)
    

class TimeTableEntry(models.Model):
    meeting = models.ForeignKey(Meeting, related_name='timetable_entries')
    title = models.CharField(max_length=200, blank=True)
    timetable_index = models.IntegerField()
    duration_in_seconds = models.PositiveIntegerField()
    is_break = models.BooleanField(default=False)
    submission = models.ForeignKey('core.Submission', null=True)
    users = models.ManyToManyField(User, through='Participation')
    
    class Meta:
        app_label = 'core'
        #unique_together = (('meeting', 'timetable_index'),)
        
    def __unicode__(self):
        return "%s, index=%s" % (self.title, self.timetable_index)
    
    @property
    def duration(self):
        return timedelta(seconds=self.duration_in_seconds)
    
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
    
    @property
    def start(self):
        if not hasattr(self, '_start'):
            self._start = self.meeting._get_start_for_index(self.timetable_index)
        return self._start
        
    @property
    def end(self):
        return self.start + self.duration

def _timetable_entry_delete_post_delete(sender, **kwargs):
    entry = kwargs['instance']
    entry.meeting.timetable_entries.filter(timetable_index__gt=entry.index).update(timetable_index=models.F('timetable_index') - 1)

post_delete.connect(_timetable_entry_delete_post_delete, sender=TimeTableEntry)

class Participation(models.Model):
    entry = models.ForeignKey(TimeTableEntry, related_name='participations')
    user = models.ForeignKey(User)
    
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
