import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import ContentType
from django.utils import timezone

from ecs.authorization import AuthorizationManager
from ecs.core.models.constants import (
    SUBMISSION_LANE_EXPEDITED, SUBMISSION_LANE_LOCALEC,
    SUBMISSION_LANE_RETROSPECTIVE_THESIS, SUBMISSION_LANE_BOARD
)
from ecs.votes.constants import PERMANENT_VOTE_RESULTS, POSITIVE_VOTE_RESULTS, NEGATIVE_VOTE_RESULTS
from ecs.meetings.models import Meeting

def get_vote_filter_q(**kwargs):
    accepted_votes = set()
    f = {}
    if kwargs.get('positive', False):
        accepted_votes |= set(POSITIVE_VOTE_RESULTS)
    if kwargs.get('negative', False):
        accepted_votes |= set(NEGATIVE_VOTE_RESULTS)
    if kwargs.get('permanent', False):
        if accepted_votes:
            accepted_votes &= set(PERMANENT_VOTE_RESULTS)
        else:
            accepted_votes = set(PERMANENT_VOTE_RESULTS)
    f['votes__result__in'] = accepted_votes
    if kwargs.get('published', True):
        f['votes__published_at__isnull'] = False
    return Q(**f)


class SubmissionQuerySet(models.QuerySet):
    def amg(self):
        return self.filter(Q(current_submission_form__project_type_non_reg_drug=True)|Q(current_submission_form__project_type_reg_drug=True))

    def mpg(self):
        return self.filter(current_submission_form__project_type_medical_device=True)
        
    def not_amg_and_not_mpg(self):
        return self.exclude(current_submission_form__project_type_medical_device=True) & self.exclude(Q(current_submission_form__project_type_non_reg_drug=True)|Q(current_submission_form__project_type_reg_drug=True))

    def amg_mpg(self):
        return self.amg() & self.mpg()

    def with_vote(self, **kwargs):
        from ecs.core.models import SubmissionForm
        return self.filter(id__in=SubmissionForm.objects.with_vote(**kwargs).values('submission_id').query)

    def expedited(self):
        return self.filter(workflow_lane=SUBMISSION_LANE_EXPEDITED)

    def localec(self):
        return self.filter(workflow_lane=SUBMISSION_LANE_LOCALEC)
        
    def for_thesis_lane(self):
        return self.filter(workflow_lane=SUBMISSION_LANE_RETROSPECTIVE_THESIS)
        
    def for_board_lane(self):
        return self.filter(workflow_lane=SUBMISSION_LANE_BOARD)

    def past_meetings(self):
        return self.filter(meetings__ended__isnull=False)

    def upcoming_meetings(self):
        return self.filter(meetings__ended=None)
    
    def next_meeting(self):
        try:
            meeting = Meeting.objects.next()
        except Meeting.DoesNotExist:
            return self.none()
        else:
            return self.filter(meetings__pk=meeting.pk)

    def no_meeting(self):
        return self.filter(meetings=None)

    def mine(self, user):
        return self.filter(Q(current_submission_form__submitter=user)|Q(current_submission_form__sponsor=user)|Q(presenter=user)|Q(susar_presenter=user)|Q(current_submission_form__primary_investigator__user=user))

    def reviewed_by_user(self, user):
        # local import to prevent circular import
        from ecs.core.models import Submission, TemporaryAuthorization
        from ecs.tasks.models import Task
        from ecs.checklists.models import Checklist

        q = Q(pk=None)
        for a in user.assigned_medical_categories.all():
            q |= Q(pk__in=a.meeting.timetable_entries.filter(submission__medical_categories=a.category).values('submission_id'))

        submission_ct = ContentType.objects.get_for_model(Submission)
        q |= Q(pk__in=Task.objects.filter(content_type=submission_ct, assigned_to=user).exclude(task_type__workflow_node__uid__in=('resubmission', 'b2_resubmission')).values('data_id'))
        checklist_ct = ContentType.objects.get_for_model(Checklist)
        q |= Q(pk__in=Checklist.objects.filter(pk__in=Task.objects.filter(content_type=checklist_ct, assigned_to=user).values('data_id')).values('submission__pk'))
        q |= Q(id__in=TemporaryAuthorization.objects.active(user=user).values('submission_id'))
        return self.filter(q).distinct()

    def none(self):
        """ Ugly hack: per default none returns an EmptyQuerySet instance which does not have our methods """
        return self.extra(where=['1=0']) 

    def for_year(self, year):
        return self.filter(ec_number__gte=year*10000, ec_number__lt=(year+1)*10000)


class SubmissionManager(AuthorizationManager.from_queryset(SubmissionQuerySet)):
    def get_base_queryset(self):
        # XXX: We really shouldn't be using distinct() here - it hurts
        # performance.
        return SubmissionQuerySet(self.model).distinct()


class SubmissionFormQuerySet(models.QuerySet):
    def current(self):
        return self.filter(submission__current_submission_form__id=models.F('id'))

    def with_vote(self, **kwargs):
        return self.filter(get_vote_filter_q(**kwargs))

    def with_any_vote(self, **kwargs):
        from ecs.core.models import Submission
        return self.filter(submission__id__in=Submission.objects.with_vote(**kwargs).values('id').query)


SubmissionFormManager = AuthorizationManager.from_queryset(SubmissionFormQuerySet)


class InvestigatorQuerySet(models.QuerySet):
    def system_ec(self):
        system_ec_uuid = uuid.UUID(settings.ETHICS_COMMISSION_UUID)
        return self.filter(ethics_commission__uuid=system_ec_uuid)

    def non_system_ec(self):
        system_ec_uuid = uuid.UUID(settings.ETHICS_COMMISSION_UUID)
        return self.exclude(ethics_commission__uuid=system_ec_uuid)


InvestigatorManager = AuthorizationManager.from_queryset(InvestigatorQuerySet)


class TemporaryAuthorizationManager(models.Manager):
    def active(self, **kwargs):
        now = timezone.now()
        return self.filter(start__lte=now, end__gt=now).filter(**kwargs)
