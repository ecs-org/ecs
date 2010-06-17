# -*- coding: utf-8 -*-
import math
from datetime import timedelta, datetime
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.contrib.auth.models import User

from ecs.core.models.core import MedicalCategory
from ecs.utils import cached_property
from ecs.utils.timedelta import timedelta_to_seconds


#impediments = p.get_impediments(time, event.duration)
#if impediments:
#    self.impediments.setdefault(p, []).extend(impediments)
#if p not in self.impediments:
#    self.impediments[p] =

class TimetableMetrics(object):
    def __init__(self, permutation, users=None):
        self.users = users

        self.waiting_time_per_user = {}
        self._waiting_time_total = 0
        self._waiting_time_min = None
        self._waiting_time_max = None

        self.constraint_violations = {}
        self.constraint_violation_total = 0
        
        self.optimal_start_diffs = {}
        self._optimal_start_diff_sum = 0
        self._optimal_start_diff_squared_sum = 0

        offset = 0
        for user in users:
            user._waiting_time = 0
            user._waiting_time_offset = None
        for entry in permutation:
            next_offset = offset + entry.duration_in_seconds
            for user in entry.users:
                if user._waiting_time_offset is not None:
                    wt = offset - user._waiting_time_offset
                    user._waiting_time += wt
                    self._waiting_time_total += wt
                user._waiting_time_offset = next_offset
                for constraint in user.constraints:
                    if constraint.offset_in_seconds < next_offset and constraint.offset_in_seconds + constraint.duration_in_seconds > offset:
                        self.constraint_violations.setdefault(constraint, 0)
                        self.constraint_violations[constraint] += constraint.weight
                        self.constraint_violation_total += constraint.weight
            if entry.optimal_start_offset is not None:
                diff = abs(offset - entry.optimal_start_offset)
                self.optimal_start_diffs[entry] = diff
                self._optimal_start_diff_squared_sum += diff * diff
                self._optimal_start_diff_sum += diff
            offset = next_offset
        
        for user in users:
            wt = user._waiting_time
            self.waiting_time_per_user[user] = timedelta(seconds=wt)
            if self._waiting_time_min is None or wt < self._waiting_time_min:
                self._waiting_time_min = wt
            if self._waiting_time_max is None or wt > self._waiting_time_max:
                self._waiting_time_max = wt
            
    def __repr__(self):
        return ", ".join("%s: %s" % (name, getattr(self, 'waiting_time_%s' % name)) for name in ('total', 'avg', 'min', 'max', 'variance'))

    @cached_property
    def waiting_time_total(self):
        s = timedelta(seconds=0)
        for time in self.waiting_time_per_user.itervalues():
            s += time
        return s
        
    @cached_property
    def waiting_time_avg(self):
        if not self.waiting_time_per_user:
            return timedelta(seconds=0)
        return self.waiting_time_total / len(self.waiting_time_per_user)
        
    @cached_property
    def waiting_time_max(self):
        if not self.waiting_time_per_user:
            return timedelta(seconds=0)
        return max(self.waiting_time_per_user.itervalues())

    @cached_property
    def waiting_time_min(self):
        if not self.waiting_time_per_user:
            return timedelta(seconds=0)
        return min(self.waiting_time_per_user.itervalues())
        
    @cached_property
    def waiting_time_variance(self):
        if not self.waiting_time_per_user:
            return timedelta(seconds=0)
        avg = timedelta_to_seconds(self.waiting_time_avg)
        var = 0
        for time in self.waiting_time_per_user.itervalues():
            d = avg - timedelta_to_seconds(time)
            var += d*d
        return timedelta(seconds=math.sqrt(var / len(self.waiting_time_per_user)))
        

class Meeting(models.Model):
    start = models.DateTimeField()
    title = models.CharField(max_length=200, blank=True)
    optimization_task_id = models.TextField(null=True)
    submissions = models.ManyToManyField('core.Submission', through='TimetableEntry', related_name='meetings')
    started = models.DateTimeField(null=True)
    ended = models.DateTimeField(null=True)
    
    class Meta:
        app_label = 'core'
        
    def __unicode__(self):
        return "%s: %s" % (self.start, self.title)
        
    @cached_property
    def duration(self):
        return timedelta(seconds=self.timetable_entries.aggregate(sum=models.Sum('duration_in_seconds'))['sum'])

    @property
    def end(self):
        return self.start + self.duration
        
    @cached_property
    def metrics(self):
        entries, users = self.timetable
        return TimetableMetrics(entries, users)
        
    def create_evaluation_func(self, func):
        entries, users = self.timetable
        def f(permutation):
            return func(TimetableMetrics(permutation, users=users))
        return f
        
    def _clear_caches(self):
        del self.metrics
        del self.duration
        del self.timetable
        del self.users_with_constraints
        
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

    @property
    def users(self):
        return User.objects.filter(meeting_participations__entry__meeting=self).distinct().order_by('username')

    @cached_property
    def users_with_constraints(self):
        constraints_by_user_id = {}
        start_date = self.start.date()
        for constraint in self.constraints.order_by('start_time'):
            start = datetime.combine(start_date, constraint.start_time)
            constraint.offset_in_seconds = timedelta_to_seconds(start - self.start)
            constraints_by_user_id.setdefault(constraint.user_id, []).append(constraint)
        users = []
        for user in self.users:
            user.constraints = constraints_by_user_id.get(user.id, [])
            users.append(user)
        return users

    @cached_property
    def timetable(self):
        duration = timedelta(seconds=0)
        users_by_entry_id = {}
        users_by_id = {}
        for user in self.users_with_constraints:
            users_by_id[user.id] = user
        entries = list()
        for participation in Participation.objects.filter(entry__meeting=self).select_related('user').order_by('user__username'):
            users_by_entry_id.setdefault(participation.entry_id, set()).add(users_by_id.get(participation.user_id))
        for entry in self.timetable_entries.select_related('submission').order_by('timetable_index'):
            entry.users = users_by_entry_id.get(entry.id, set())
            entry.start = self.start + duration
            duration += entry.duration
            entry.end = self.start + duration
            entries.append(entry)
        return tuple(entries), set(users_by_id.itervalues())
        
    def __iter__(self):
        entries, users = self.timetable
        return iter(entries)
        
    def _get_start_for_index(self, index):
        offset = self.timetable_entries.filter(timetable_index__lt=index).aggregate(sum=models.Sum('duration_in_seconds'))['sum']
        return self.start + timedelta(seconds=offset or 0)
    
    def _apply_permutation(self, permutation):
        assert set(self) == set(permutation)
        for i, entry in enumerate(permutation):
            entry.timetable_index = i
            entry.save()
        self._clear_caches()
        
    def sort_timetable(self, func):
        perm = func(tuple(self))
        self._apply_permutation(perm)
    
    @property
    def open_tops(self):
        return self.timetable_entries.filter(is_open=True)
        
    @property
    def open_tops_with_vote(self):
        return self.timetable_entries.filter(is_open=True, vote__result__isnull=False)
        

class TimetableEntry(models.Model):
    meeting = models.ForeignKey(Meeting, related_name='timetable_entries')
    title = models.CharField(max_length=200, blank=True)
    timetable_index = models.IntegerField()
    duration_in_seconds = models.PositiveIntegerField()
    is_break = models.BooleanField(default=False)
    submission = models.ForeignKey('core.Submission', null=True, related_name='timetable_entries')
    sponsor_invited = models.BooleanField(default=False)
    optimal_start = models.TimeField(null=True)
    is_open = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'core'
        #unique_together = (('meeting', 'timetable_index'),)
        
    def __unicode__(self):
        return "TOP %s" % (self.index + 1)
    
    
    def _get_duration(self):
        return timedelta(seconds=self.duration_in_seconds)
        
    def _set_duration(self, d):
        self.duration_in_seconds = int(timedelta_to_seconds(d))
    
    duration = property(_get_duration, _set_duration)
    
    @cached_property
    def optimal_start_offset(self):
        if self.optimal_start is None:
            return None
        return timedelta_to_seconds(datetime.combine(self.meeting.start.date(), self.optimal_start) - self.meeting.start)
    
    @cached_property
    def users(self):
        return User.objects.filter(meeting_participations__entry=self).order_by('username').distinct()
        
    def add_user(self, user, medical_category=None):
        Participation.objects.get_or_create(user=user, entry=self, medical_category=medical_category)
        
    def remove_user(self, user, medical_category=False):
        participations = Participation.objects.filter(user=user, entry=self)
        if medical_category is not False:
            participations = participations.filter(medical_category=medical_category)
        participations.delete()
    
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
        self.meeting._clear_caches()
    
    index = property(_get_index, _set_index)
    
    @cached_property
    def start(self):
        return self.meeting._get_start_for_index(self.timetable_index)
        
    @cached_property
    def end(self):
        return self.start + self.duration

    @cached_property
    def medical_categories(self):
        if not self.submission:
            return MedicalCategory.objects.none()
        return MedicalCategory.objects.filter(submissions__timetable_entries=self)
        
    @cached_property
    def users_by_medical_category(self):
        users_by_category = {}
        for cat in self.medical_categories:
            users_by_category.setdefault(cat, [])
        for p in self.participations.select_related('user', 'medical_category'):
            users_by_category.setdefault(p.medical_category, []).append(p.user)
            p.user.participation = p
        return users_by_category

    @cached_property
    def is_retrospective(self):
        return self.submission.retrospective
    
    @cached_property
    def is_thesis(self):
        return self.submission.thesis
        
    @cached_property
    def is_expedited(self):
        return self.submission.expedited
    
    @property
    def is_batch_processed(self):
        return self.is_thesis or self.is_expedited or self.is_retrospective
        
    @property
    def next(self):
        try:
            return self.meeting[self.index + 1]
        except IndexError:
            return None
    
    @property
    def previous(self):
        try:
            return self.meeting[self.index - 1]
        except IndexError:
            return None
        
    @property
    def next_open(self):
        entries = self.meeting.timetable_entries.filter(timetable_index__gt=self.index).filter(is_open=True).order_by('timetable_index')[:1]
        if entries:
            return entries[0]
        return None
        
    @property
    def previous_open(self):
        entries = self.meeting.timetable_entries.filter(timetable_index__lt=self.index).filter(is_open=True).order_by('-timetable_index')[:1]
        if entries:
            return entries[0]
        return None

def _timetable_entry_delete_post_delete(sender, **kwargs):
    entry = kwargs['instance']
    entry.meeting.timetable_entries.filter(timetable_index__gt=entry.index).update(timetable_index=models.F('timetable_index') - 1)

post_delete.connect(_timetable_entry_delete_post_delete, sender=TimetableEntry)

class Participation(models.Model):
    entry = models.ForeignKey(TimetableEntry, related_name='participations')
    user = models.ForeignKey(User, related_name='meeting_participations')
    medical_category = models.ForeignKey(MedicalCategory, related_name='meeting_participations', null=True, blank=True)
    
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
        
    @property
    def duration(self):
        d = datetime.now().date()
        return datetime.combine(d, self.end_time) - datetime.combine(d, self.start_time)

    @cached_property
    def duration_in_seconds(self):
        return timedelta_to_seconds(self.duration)
   

