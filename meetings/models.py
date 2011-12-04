# -*- coding: utf-8 -*-
import math
from datetime import timedelta, datetime
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ecs.authorization import AuthorizationManager
from ecs.core.models.core import MedicalCategory
from ecs.core.models.constants import SUBMISSION_LANE_RETROSPECTIVE_THESIS, SUBMISSION_LANE_EXPEDITED, SUBMISSION_LANE_LOCALEC
from ecs.utils import cached_property
from ecs.utils.timedelta import timedelta_to_seconds
from ecs.utils.viewutils import render_pdf
from ecs.tasks.models import TaskType
from ecs.votes.models import Vote


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
            for user, ignored in entry.users:
                if ignored:
                    continue
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
        

class AssignedMedicalCategory(models.Model):
    category = models.ForeignKey('core.MedicalCategory')
    board_member = models.ForeignKey(User, null=True, blank=True, related_name='assigned_medical_categories')
    meeting = models.ForeignKey('meetings.Meeting', related_name='medical_categories')

    objects = AuthorizationManager()

    class Meta:
        unique_together = (('category', 'meeting'),)

    def __unicode__(self):
        return '%s - %s' % (self.meeting.title, self.category.name)

class MeetingManager(AuthorizationManager):
    def next(self):
        now = datetime.now()
        dday = datetime(year=now.year, month=now.month, day=now.day) + timedelta(days=1)
        try:
            return self.filter(start__gt=dday).order_by('start')[0]
        except IndexError:
            raise self.model.DoesNotExist()

    def next_schedulable_meeting(self, submission):
        sf = submission.current_submission_form
        is_thesis = submission.workflow_lane == SUBMISSION_LANE_RETROSPECTIVE_THESIS

        meetings = self.filter(deadline__gt=sf.created_at)
        if is_thesis:
            meetings = self.filter(deadline_diplomathesis__gt=sf.created_at)

        try:
            return meetings.filter(started=None).order_by('start')[0]
        except IndexError:
            last_meeting = meetings.all().order_by('-start')[0]
            new_start = last_meeting.start
            new_deadline = last_meeting.deadline
            new_deadline_diplomathesis = last_meeting.deadline_diplomathesis
            while True:
                new_start += timedelta(days=30)
                new_deadline += timedelta(days=30)
                new_deadline_diplomathesis += timedelta(days=30)
                if (not is_thesis and datetime.now() < new_deadline) or \
                    (is_thesis and datetime.now() < new_deadline_diplomathesis):
                    title = new_start.strftime('%B Meeting %Y')
                    m = Meeting.objects.create(start=new_start, deadline=new_deadline,
                        deadline_diplomathesis=new_deadline_diplomathesis, title=title)
                    return m

class Meeting(models.Model):
    start = models.DateTimeField()
    title = models.CharField(max_length=200)
    optimization_task_id = models.TextField(null=True)
    submissions = models.ManyToManyField('core.Submission', through='TimetableEntry', related_name='meetings')
    started = models.DateTimeField(null=True)
    ended = models.DateTimeField(null=True)
    comments = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField(null=True)
    deadline_diplomathesis = models.DateTimeField(null=True)

    objects = MeetingManager()
    

    @property
    def retrospective_thesis_submissions(self):
        return self.submissions.filter(workflow_lane=SUBMISSION_LANE_RETROSPECTIVE_THESIS)

    @property
    def expedited_submissions(self):
        return self.submissions.filter(workflow_lane=SUBMISSION_LANE_EXPEDITED)

    @property
    def localec_submissions(self):
        return self.submissions.filter(workflow_lane=SUBMISSION_LANE_LOCALEC)

    @property
    def retrospective_thesis_entries(self):
        return self.timetable_entries.filter(submission__workflow_lane=SUBMISSION_LANE_RETROSPECTIVE_THESIS)

    @property
    def expedited_entries(self):
        return self.timetable_entries.filter(submission__workflow_lane=SUBMISSION_LANE_EXPEDITED)

    @property
    def localec_entries(self):
        return self.timetable_entries.filter(submission__workflow_lane=SUBMISSION_LANE_LOCALEC)

    def __unicode__(self):
        return "%s: %s" % (self.start, self.title)
        
    def save(self, **kwargs):
        return super(Meeting, self).save(**kwargs)
        
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
        del self.timetable_entries_which_violate_constraints

    def create_boardmember_reviews(self):
        task_type = TaskType.objects.get(workflow_node__uid='board_member_review', workflow_node__graph__auto_start=True)
        for amc in self.medical_categories.all():
            if not amc.board_member:
                continue
            for entry in self.timetable_entries.filter(submission__medical_categories=amc.category).distinct():
                # add participations for all timetable entries with matching categories.
                participation, created = Participation.objects.get_or_create(medical_category=amc.category, entry=entry, user=amc.board_member)
                if created:
                    # create board member review task
                    token = task_type.workflow_node.bind(entry.submission.workflow.workflows[0]).receive_token(None)
                    token.task.accept(user=amc.board_member)
            
    def add_entry(self, **kwargs):
        visible = kwargs.pop('visible', True)
        if visible:
            last_index = self.timetable_entries.aggregate(models.Max('timetable_index'))['timetable_index__max']
            if last_index is None:
                kwargs['timetable_index'] = 0
            else:
                kwargs['timetable_index'] = last_index + 1
        else:
            kwargs['timetable_index'] = None
        duration = kwargs.pop('duration', None)
        if duration is not None:
            kwargs['duration_in_seconds'] = duration.seconds
        entry = self.timetable_entries.create(**kwargs)
        self._clear_caches()
        self.create_boardmember_reviews()
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
        return self.timetable_entries.filter(timetable_index__isnull=False).count()

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
    def timetable_entries_which_violate_constraints(self):
        start_date = self.start.date()
        start_data = self.start.date()
        entries_which_violate_constraints = []
        for constraint in self.constraints.all():
            constraint_start = datetime.combine(start_date, constraint.start_time)
            constraint_end = datetime.combine(start_date, constraint.end_time)
            for participation in Participation.objects.filter(user=constraint.user, ignored_for_optimization=False):
                start = participation.entry.start
                end = participation.entry.end
                if (constraint_start >= start and constraint_start < end) or \
                    (constraint_end > start and constraint_end < end) or \
                    (constraint_start <= start and constraint_end >= end):
                    entries_which_violate_constraints.append(participation.entry)
        return entries_which_violate_constraints

    @cached_property
    def timetable(self):
        duration = timedelta(seconds=0)
        users_by_entry_id = {}
        users_by_id = {}
        for user in self.users_with_constraints:
            users_by_id[user.id] = user
        entries = list()
        for participation in Participation.objects.filter(entry__meeting=self).select_related('user').order_by('user__username'):
            users_by_entry_id.setdefault(participation.entry_id, set()).add((users_by_id.get(participation.user_id), participation.ignored_for_optimization))
        for entry in self.timetable_entries.filter(timetable_index__isnull=False).select_related('submission').order_by('timetable_index'):
            entry.users = users_by_entry_id.get(entry.id, set())
            entry.has_ignored_participations = any(ignored for user, ignored in entry.users)
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
        return self.timetable_entries.filter(timetable_index__isnull=False, is_open=True)
        
    @property
    def open_tops_with_vote(self):
        return self.timetable_entries.filter(timetable_index__isnull=False, is_open=True, vote__result__isnull=False)

    def __nonzero__(self):
        return True   # work around a django bug

    def get_agenda_pdf(self, request):
        rts = list(self.retrospective_thesis_entries.all())
        es = list(self.expedited_entries.all())
        ls = list(self.localec_entries.all())

        return render_pdf(request, 'db/meetings/wkhtml2pdf/agenda.html', {
            'meeting': self,
            'additional_tops': enumerate(rts + es + ls, len(self)+1),
        })
        
    def get_protocol_pdf(self, request):
        timetable_entries = self.timetable_entries.filter(timetable_index__isnull=False).order_by('timetable_index')
        tops = []
        for top in timetable_entries:
            try:
                vote = Vote.objects.filter(top=top)[0]
            except IndexError:
                vote = None
            tops.append((top, vote,))

        b2_votes = Vote.objects.filter(result='2', top__in=timetable_entries)
        submission_forms = [x.submission_form for x in b2_votes]
        b1ized = Vote.objects.filter(result='1', submission_form__in=submission_forms).order_by('submission_form__submission__ec_number')

        rts = list(self.retrospective_thesis_entries.all())
        es = list(self.expedited_entries.all())
        ls = list(self.localec_entries.all())
        additional_tops = []
        for i, top in enumerate(rts + es + ls, len(tops) + 1):
            try:
                vote = Vote.objects.filter(top=top)[0]
            except IndexError:
                vote = None
            additional_tops.append((i, top, vote,))

        return render_pdf(request, 'db/meetings/wkhtml2pdf/protocol.html', {
            'meeting': self,
            'tops': tops,
            'b1ized': b1ized,
            'additional_tops': additional_tops,
        })

    def _get_timeframe_for_user(self, user):
        entries = list(self.timetable_entries.filter(participations__user=user).order_by('timetable_index'))
        start = entries[0].start
        start -= timedelta(minutes=start.minute%10)
        end = entries[-1].end
        if end.minute % 10 > 0:
            end += timedelta(minutes=10-end.minute%10)
        return (start, end)

    def get_timetable_pdf(self, request):
        timetable = {}
        for entry in self:
            for user, ignored in entry.users:
                if user in timetable:
                    timetable[user].append(entry)
                else:
                    timetable[user] = [entry]

        timetable = sorted([{
            'user': key,
            'entries': sorted(timetable[key], key=lambda x:x.timetable_index),
        } for key in timetable], key=lambda x:x['user'])

        for row in timetable:
            start, end = self._get_timeframe_for_user(row['user'])
            row['time'] = '{0} - {1}'.format(start.strftime('%H:%M'), end.strftime('%H:%M'))

        return render_pdf(request, 'db/meetings/wkhtml2pdf/timetable.html', {
            'meeting': self,
            'timetable': timetable,
        })
        
    def get_medical_categories(self):
        return MedicalCategory.objects.filter(submissions__timetable_entries__meeting=self)
        
    def update_assigned_categories(self):
        old_assignments = {}
        for amc in AssignedMedicalCategory.objects.filter(meeting=self):
            old_assignments[amc.category_id] = amc
        new_assignments = {}
        for cat in self.get_medical_categories():
            if cat.pk in old_assignments:
                del old_assignments[cat.pk]
            else:
                AssignedMedicalCategory.objects.get_or_create(meeting=self, category=cat)
        AssignedMedicalCategory.objects.filter(pk__in=[amc.pk for amc in old_assignments.itervalues()]).delete()
        Participation.objects.filter(entry__meeting=self).filter(medical_category__pk__in=old_assignments.keys()).delete()


class TimetableEntry(models.Model):
    meeting = models.ForeignKey(Meeting, related_name='timetable_entries')
    title = models.CharField(max_length=200, blank=True)
    timetable_index = models.IntegerField(null=True)
    duration_in_seconds = models.PositiveIntegerField()
    is_break = models.BooleanField(default=False)
    submission = models.ForeignKey('core.Submission', null=True, related_name='timetable_entries')
    optimal_start = models.TimeField(null=True)
    is_open = models.BooleanField(default=True)

    objects = AuthorizationManager()

    def __unicode__(self):
        if self.index is not None:
            return u"TOP %s" % (self.index + 1)
        else:
            return u"TOP"
    
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
        
    def _set_index(self, index):
        sid = transaction.savepoint()
        try:
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
        except Exception, e:
            transaction.savepoint_rollback(sid)
            raise e
        else:
            transaction.savepoint_commit(sid)
    
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

    @property
    def is_batch_processed(self):
        return bool(self.submission_id) and not self.submission.is_regular
        
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
    
    def _collect_users(self, padding, r):
        users = set()
        offset = timedelta()
        for i in r:
            entry = self.meeting[i]
            users.update(entry.users)
            offset += entry.duration
            if offset >= padding:
                break
        return users
    
    @cached_property
    def broetchen(self, padding_before=timedelta(hours=1), padding_after=timedelta(hours=1)):
        waiting_users = set(User.objects.filter(
                meeting_participations__entry__meeting=self.meeting, 
                meeting_participations__entry__timetable_index__lte=self.timetable_index,
            ).filter(
                meeting_participations__entry__meeting=self.meeting, 
                meeting_participations__entry__timetable_index__gte=self.timetable_index,
            ).distinct()
        )
        before = self._collect_users(padding_before, xrange(self.index - 1, -1, -1)).difference(waiting_users)
        after = self._collect_users(padding_after, xrange(self.index + 1, len(self.meeting))).difference(waiting_users)
        return len(before), len(waiting_users), len(after)

    def refresh(self, **kwargs):
        visible = kwargs.pop('visible', True)
        previous_index = self.timetable_index
        to_visible = visible and previous_index is None
        from_visible = not visible and not previous_index is None
        if to_visible:
            last_index = self.meeting.timetable_entries.aggregate(models.Max('timetable_index'))['timetable_index__max']
            if last_index is None:
                kwargs['timetable_index'] = 0
            else:
                kwargs['timetable_index'] = last_index + 1
        elif from_visible:
            kwargs['timetable_index'] = None
        duration = kwargs.pop('duration', None)
        if duration is not None:
            kwargs['duration_in_seconds'] = duration.seconds
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.save()
        if from_visible:
            for i, entry in enumerate(self.meeting.timetable_entries.filter(timetable_index__gt=previous_index).order_by('timetable_index')):
                entry.timetable_index = i
                entry.save()
        self.meeting._clear_caches()
        self.meeting.create_boardmember_reviews()

def _timetable_entry_post_delete(sender, **kwargs):
    entry = kwargs['instance']
    if not entry.timetable_index is None:
        entry.meeting.timetable_entries.filter(timetable_index__gt=entry.index).update(timetable_index=models.F('timetable_index') - 1)
    entry.meeting.update_assigned_categories()
    if entry.submission:
        entry.submission.update_next_meeting()

def _timetable_entry_post_save(sender, **kwargs):
    entry = kwargs['instance']
    entry.meeting.update_assigned_categories()
    if entry.submission:
        entry.submission.update_next_meeting()

post_delete.connect(_timetable_entry_post_delete, sender=TimetableEntry)
post_save.connect(_timetable_entry_post_save, sender=TimetableEntry)

class Participation(models.Model):
    entry = models.ForeignKey(TimetableEntry, related_name='participations')
    user = models.ForeignKey(User, related_name='meeting_participations')
    medical_category = models.ForeignKey(MedicalCategory, related_name='meeting_participations', null=True, blank=True)
    ignored_for_optimization = models.BooleanField(default=False)

    objects = AuthorizationManager()

WEIGHT_CHOICES = (
    (1.0, _('impossible')),
    (0.5, _('unfavorable')),
)

class Constraint(models.Model):
    meeting = models.ForeignKey(Meeting, related_name='constraints')
    user = models.ForeignKey(User, related_name='meeting_constraints')
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    weight = models.FloatField(default=0.5, choices=WEIGHT_CHOICES)

    objects = AuthorizationManager()

    @property
    def duration(self):
        d = datetime.now().date()
        return datetime.combine(d, self.end_time) - datetime.combine(d, self.start_time)

    @cached_property
    def duration_in_seconds(self):
        return timedelta_to_seconds(self.duration)
