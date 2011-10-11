from datetime import datetime
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import ContentType
from ecs.authorization import AuthorizationManager
from ecs.core.models.constants import (
    VOTE_RESULTS, PERMANENT_VOTE_RESULTS, POSITIVE_VOTE_RESULTS, NEGATIVE_VOTE_RESULTS,
    SUBMISSION_TYPE_MULTICENTRIC_LOCAL, 
)


def get_vote_filter_q(prefix, *args, **kwargs):
    accepted_votes = set()
    f = {}
    prefix = ('%s__' % prefix) if prefix else ''
    if kwargs.get('positive', False):
        accepted_votes |= set(POSITIVE_VOTE_RESULTS)
    if kwargs.get('negative', False):
        accepted_votes |= set(NEGATIVE_VOTE_RESULTS)
    if kwargs.get('permanent', False):
        if accepted_votes:
            accepted_votes &= set(PERMANENT_VOTE_RESULTS)
        else:
            accepted_votes = set(PERMANENT_VOTE_RESULTS)
    f['%svotes__result__in' % prefix] = accepted_votes
    if kwargs.get('published', True):
        f['%svotes__published_at__isnull' % prefix] = False
    if kwargs.get('valid', True):
        f['%svotes__valid_until__gte' % prefix] = datetime.now()
    for key, value in kwargs.iteritems():
        if key.startswith('valid_until'):
            f['%svotes__%s' % (prefix, key)] = value
    return Q(**f)


class SubmissionQuerySet(models.query.QuerySet):
    def amg(self):
        return self.filter(Q(is_amg=True) | (
            Q(is_amg=None) & (
                Q(current_submission_form__project_type_non_reg_drug=True)
                | Q(current_submission_form__project_type_reg_drug=True)
            )
        ))

    def mpg(self):
        return self.filter(Q(is_mpg=True) | (
            Q(is_mpg=None) & Q(current_submission_form__project_type_medical_device=True)
        ))

    def amg_mpg(self):
        return self.amg() & self.mpg()
    
    def with_vote(self, *args, **kwargs):
        return self.filter(get_vote_filter_q('forms', *args, **kwargs))

    def b1(self):
        return self.filter(Q(forms__current_published_vote__isnull=False, forms__current_published_vote__result='1')|Q(forms__current_pending_vote__isnull=False, forms__current_pending_vote__result='1'), current_submission_form__isnull=False)

    def b2(self):
        return self.filter(Q(forms__current_published_vote__isnull=False, forms__current_published_vote__result='2')|Q(forms__current_pending_vote__isnull=False, forms__current_pending_vote__result='2'), current_submission_form__isnull=False)

    def b3(self):
        return self.filter(Q(forms__current_published_vote__isnull=False, forms__current_published_vote__result__in=['3a', '3b'])|Q(forms__current_pending_vote__isnull=False, forms__current_pending_vote__result__in=['3a', '3b']), current_submission_form__isnull=False)

    def b4(self):
        return self.filter(Q(forms__current_published_vote__isnull=False, forms__current_published_vote__result='4')|Q(forms__current_pending_vote__isnull=False, forms__current_pending_vote__result='4'), current_submission_form__isnull=False)

    def b5(self):
        return self.filter(Q(forms__current_published_vote__isnull=False, forms__current_published_vote__result='5')|Q(forms__current_pending_vote__isnull=False, forms__current_pending_vote__result='5'), current_submission_form__isnull=False)

    def new(self):
        return self.filter(meetings__isnull=True)

    def thesis(self):
        return self.filter(Q(thesis=True)|(Q(thesis=None) & ~Q(current_submission_form__project_type_education_context=None)))

    def retrospective(self):
        return self.filter(Q(retrospective=True)|Q(retrospective=None, current_submission_form__project_type_retrospective=True))

    def retrospective_thesis(self):
        return self.filter(Q(pk__in=self.thesis().values('pk').query) & Q(pk__in=self.retrospective().values('pk').query))

    def expedited(self):
        return self.filter(expedited=True)

    def localec(self):
        return self.filter(current_submission_form__submission_type=SUBMISSION_TYPE_MULTICENTRIC_LOCAL)

    def next_meeting(self):
        from ecs.meetings.models import Meeting
        try:
            meeting = Meeting.objects.filter(start__gt=datetime.now()).order_by('start')[0]
        except IndexError:
            return self.none()
        else:
            return self.filter(meetings__pk=meeting.pk)

    def mine(self, user):
        return self.filter(Q(current_submission_form__submitter=user)|Q(current_submission_form__sponsor=user)|Q(current_submission_form__presenter=user)|Q(current_submission_form__susar_presenter=user))

    def reviewed_by_user(self, user):
        submissions = self.none()
        for a in user.assigned_medical_categories.all():
            submissions |= self.filter(pk__in=a.meeting.submissions.filter(medical_categories=a.category).values('pk').query)

        from ecs.core.models.submissions import Submission
        submission_ct = ContentType.objects.get_for_model(Submission)
        from ecs.tasks.models import Task
        submissions |= self.filter(pk__in=Task.objects.filter(content_type=submission_ct, assigned_to=user).exclude(task_type__workflow_node__uid='resubmission').values('data_id').query)
        from ecs.core.models import Checklist
        checklist_ct = ContentType.objects.get_for_model(Checklist)
        submissions |= self.filter(pk__in=Checklist.objects.filter(pk__in=Task.objects.filter(content_type=checklist_ct, assigned_to=user).values('data_id').query).values('submission__pk').query)
        return submissions.distinct()

    def none(self):
        """ Ugly hack: per default none returns an EmptyQuerySet instance which does not have our methods """
        return self.extra(where=['1=0']) 


class SubmissionManager(AuthorizationManager):
    def get_base_query_set(self):
        return SubmissionQuerySet(self.model).distinct()

    def amg(self):
        return self.all().amg()

    def mpg(self):
        return self.all().mpg()

    def amg_mpg(self):
        return self.all().amg_mpg()

    def new(self):
        return self.all().new()

    def with_vote(self, *args, **kwargs):
        return self.all().with_vote(*args, **kwargs)

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

    def next_meeting(self):
        return self.all().next_meeting()

    def mine(self, user):
        return self.all().mine(user)

    def reviewed_by_user(self, user):
        return self.all().reviewed_by_user(user)

    def none(self):
        return self.all().none()


class SubmissionFormQuerySet(models.query.QuerySet):
    def current(self):
        return self.filter(submission__current_submission_form__id=models.F('id'))

    def with_vote(self, **kwargs):
        return self.filter(get_vote_filter_q(None, **kwargs))


class SubmissionFormManager(AuthorizationManager):
    def get_base_query_set(self):
        return SubmissionFormQuerySet(self.model)
        
    def current(self):
        return self.all().current()
        
    def with_vote(self, *args, **kwargs):
        return self.all().with_vote(*args, **kwargs)


class VoteQuerySet(models.query.QuerySet):
    def positive(self):
        return self.filter(result__in=POSITIVE_VOTE_RESULTS)
        
    def negative(self):
        return self.filter(result__in=NEGATIVE_VOTE_RESULTS)
        
    def permanent(self):
        return self.filter(result__in=PERMANENT_VOTE_RESULTS)


class VoteManager(AuthorizationManager):
    def get_base_query_set(self):
        return VoteQuerySet(self.model)

    def positive(self):
        return self.all().positive()

    def negative(self):
        return self.all().negative()

    def permanent(self):
        return self.all().permanent()

