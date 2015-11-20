from datetime import datetime
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import ContentType
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


class SubmissionQuerySet(models.query.QuerySet):
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

    def _with_explicit_vote(self, *results, **kwargs):
        q = Q(current_submission_form__current_published_vote__isnull=False, current_submission_form__current_published_vote__result__in=results)
        if kwargs.get('include_pending', True):
            q |= Q(current_submission_form__current_pending_vote__isnull=False, current_submission_form__current_pending_vote__result__in=results)
        return self.filter(q, current_submission_form__isnull=False)

    def b1(self, include_pending=True):
        return self._with_explicit_vote('1', include_pending=include_pending)

    def b2(self, include_pending=True):
        return self._with_explicit_vote('2', include_pending=include_pending)

    def b3(self, include_pending=True):
        return self._with_explicit_vote('3a', '3b', include_pending=include_pending)

    def b4(self, include_pending=True):
        return self._with_explicit_vote('4', include_pending=include_pending)

    def b5(self, include_pending=True):
        return self._with_explicit_vote('5', include_pending=include_pending)
        
    def without_vote(self, include_pending=True):
        q = ~Q(forms__current_published_vote__isnull=False)
        if include_pending:
            q &= Q(forms__current_pending_vote__isnull=True)
        return self.filter(q, current_submission_form__isnull=False)

    def new(self):
        return self.filter(meetings__isnull=True)

    def thesis(self):
        return self.exclude(current_submission_form__project_type_education_context=None)

    def retrospective(self):
        return self.filter(current_submission_form__project_type_retrospective=True)

    def retrospective_thesis(self):
        return self.filter(Q(pk__in=self.thesis().values('pk').query) & Q(pk__in=self.retrospective().values('pk').query))

    def expedited(self):
        return self.filter(workflow_lane=SUBMISSION_LANE_EXPEDITED)

    def localec(self):
        return self.filter(workflow_lane=SUBMISSION_LANE_LOCALEC)
        
    def for_thesis_lane(self):
        return self.filter(workflow_lane=SUBMISSION_LANE_RETROSPECTIVE_THESIS)
        
    def for_board_lane(self):
        return self.filter(workflow_lane=SUBMISSION_LANE_BOARD)

    def past_meetings(self):
        return self.filter(meetings__pk__in=Meeting.objects.past().values('pk').query)

    def upcoming_meetings(self):
        return self.filter(meetings__pk__in=Meeting.objects.upcoming().values('pk').query)
    
    def next_meeting(self):
        try:
            meeting = Meeting.objects.next()
        except Meeting.DoesNotExist:
            return self.none()
        else:
            return self.filter(meetings__pk=meeting.pk)

    def no_meeting(self):
        return self.filter(meetings__isnull=True)

    def mine(self, user):
        return self.filter(Q(current_submission_form__submitter=user)|Q(current_submission_form__sponsor=user)|Q(presenter=user)|Q(susar_presenter=user)|Q(current_submission_form__primary_investigator__user=user))

    def reviewed_by_user(self, user):
        # local import to prevent circular import
        from ecs.core.models import Submission, TemporaryAuthorization
        from ecs.tasks.models import Task
        from ecs.checklists.models import Checklist

        submissions = self.none()
        for a in user.assigned_medical_categories.all():
            submissions |= self.filter(pk__in=a.meeting.submissions.filter(medical_categories=a.category).values('pk').query)

        submission_ct = ContentType.objects.get_for_model(Submission)
        submissions |= self.filter(pk__in=Task.objects.filter(content_type=submission_ct, assigned_to=user).exclude(task_type__workflow_node__uid='resubmission').values('data_id').query)
        checklist_ct = ContentType.objects.get_for_model(Checklist)
        submissions |= self.filter(pk__in=Checklist.objects.filter(pk__in=Task.objects.filter(content_type=checklist_ct, assigned_to=user).values('data_id').query).values('submission__pk').query)
        submissions |= self.filter(id__in=TemporaryAuthorization.objects.active(user=user).values('submission_id').query)
        return submissions.distinct()

    def none(self):
        """ Ugly hack: per default none returns an EmptyQuerySet instance which does not have our methods """
        return self.extra(where=['1=0']) 

    def for_year(self, year):
        return self.filter(ec_number__gte=year*10000, ec_number__lt=(year+1)*10000)


class SubmissionManager(AuthorizationManager):
    def get_base_query_set(self):
        return SubmissionQuerySet(self.model).distinct()

    def amg(self):
        return self.all().amg()

    def mpg(self):
        return self.all().mpg()

    def amg_mpg(self):
        return self.all().amg_mpg()
        
    def not_amg_and_not_mpg(self):
        return self.all().not_amg_and_not_mpg()

    def with_vote(self, **kwargs):
        return self.all().with_vote(**kwargs)

    def new(self):
        return self.all().new()

    def b1(self):
        return self.all().b1()

    def b2(self):
        return self.all().b2()

    def b3(self):
        return self.all().b3()

    def b4(self):
        return self.all().b4()

    def b5(self):
        return self.all().b5()

    def thesis(self):
        return self.all().thesis()

    def retrospective(self):
        return self.all().retrospective()

    def retrospective_thesis(self):
        return self.all().retrospective_thesis()

    def expedited(self):
        return self.all().expedited()

    def localec(self):
        return self.all().localec()

    def past_meetings(self):
        return self.all().past_meetings()

    def upcoming_meetings(self):
        return self.all().upcoming_meetings()

    def next_meeting(self):
        return self.all().next_meeting()

    def no_meeting(self):
        return self.all().no_meeting()

    def mine(self, user):
        return self.all().mine(user)

    def reviewed_by_user(self, user):
        return self.all().reviewed_by_user(user)

    def none(self):
        return self.all().none()
        
    def for_thesis_lane(self):
        return self.all().for_thesis_lane()
        
    def for_board_lane(self):
        return self.all().for_board_lane()

    def for_year(self, year):
        return self.all().for_year(year)


class SubmissionFormQuerySet(models.query.QuerySet):
    def current(self):
        return self.filter(submission__current_submission_form__id=models.F('id'))

    def with_vote(self, **kwargs):
        return self.filter(get_vote_filter_q(**kwargs))

    def with_any_vote(self, **kwargs):
        from ecs.core.models import Submission
        return self.filter(submission__id__in=Submission.objects.with_vote(**kwargs).values('id').query)

class SubmissionFormManager(AuthorizationManager):
    def get_base_query_set(self):
        return SubmissionFormQuerySet(self.model)
        
    def current(self):
        return self.all().current()
        
    def with_vote(self, **kwargs):
        return self.all().with_vote(**kwargs)
        
    def with_any_vote(self, **kwargs):
        return self.all().with_any_vote(**kwargs)


class TemporaryAuthorizationManager(models.Manager):
    def active(self, **kwargs):
        now = datetime.now()
        return self.filter(start__lte=now, end__gt=now).filter(**kwargs)
