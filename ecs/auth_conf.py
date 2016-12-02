from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from ecs import authorization
from ecs.core.models import (Submission, SubmissionForm, Investigator,
    Measure, TemporaryAuthorization, MySubmission)
from ecs.checklists.models import Checklist, ChecklistAnswer
from ecs.votes.models import Vote
from ecs.tasks.models import Task, TaskType
from ecs.notifications.models import Notification, AmendmentNotification, SafetyNotification, NotificationAnswer, NOTIFICATION_MODELS
from ecs.meetings.models import Meeting, TimetableEntry, Participation
from ecs.votes.constants import PERMANENT_VOTE_RESULTS


class SubmissionQFactory(authorization.QFactory):
    def get_q(self, user):
        ### internal users can see all submissions
        if user.is_staff or user.profile.is_internal:
            return self.make_q()

        q = self.make_q(id__in=
            MySubmission.objects.filter(user_id=user.id)
                .values('submission_id')
        )
        
        ### explicit temporary permissions
        q |= self.make_q(id__in=
            TemporaryAuthorization.objects.active(user=user)
                .values('submission_id')
        )

        ### permissions until final vote is published
        until_vote_q = self.make_q(
            pk__in=Checklist.objects.values('submission__pk'))
        until_vote_q |= self.make_q(pk__in=
            Task.objects.filter(
                content_type=ContentType.objects.get_for_model(Submission),
            ).values('data_id')
        )
        q |= until_vote_q & ~self.make_q(current_published_vote__result__in=PERMANENT_VOTE_RESULTS)

        notification_cts = map(ContentType.objects.get_for_model,
            (AmendmentNotification, SafetyNotification))
        q |= self.make_q(forms__notifications__pk__in=
            Task.objects.filter(content_type__in=notification_cts).open()
                .values('data_id'))

        return q

authorization.register(Submission, factory=SubmissionQFactory)
authorization.register(SubmissionForm, lookup='submission')
authorization.register(Investigator, lookup='submission_form__submission')
authorization.register(Measure, lookup='submission_form__submission')

class VoteQFactory(authorization.QFactory):
    def get_q(self, user):
        q = self.make_q(
            submission_form__submission__pk__in=Submission.objects.values('pk')
        )
        if not user.profile.is_internal:
            q &= self.make_q(published_at__isnull=False)
        return q

authorization.register(Vote, factory=VoteQFactory)

class TaskQFactory(authorization.QFactory):
    def get_q(self, user):
        task_types = TaskType.objects.filter(
            ~Q(group__name__in=(
                'EC-Executive Board Member', 'EC-Office', 'EC-Signing')) |
            Q(workflow_node__uid__in=user.profile.task_uids),
            group__in=user.groups.values('pk')
        )

        q = self.make_q(task_type__in=task_types.values('pk')) & (
            self.make_q(assigned_to=None) |
            self.make_q(assigned_to__profile__is_indisposed=True)
        ) & (
            self.make_q(medical_category=None) |
            self.make_q(medical_category__in=user.medical_categories.values('pk'))
        ) & ~self.make_q(review_for__assigned_to=user)
        q |= self.make_q(assigned_to=user)
        return q

authorization.register(Task, factory=TaskQFactory)

class NotificationQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q(
            submission_forms__submission__in=Submission.objects.values('pk')
        )

for cls in NOTIFICATION_MODELS:
    authorization.register(cls, factory=NotificationQFactory)

class NotificationAnswerQFactory(authorization.QFactory):
    def get_q(self, user):
        q = self.make_q(notification__in=Notification.objects.values('pk'))
        if not user.profile.is_internal:
            q &= self.make_q(published_at__isnull=False)
        notification_cts = map(ContentType.objects.get_for_model,
            NOTIFICATION_MODELS)
        q |= self.make_q(notification__in=
            Notification.objects.filter(pk__in=
                Task.objects.filter(content_type__in=notification_cts)
                    .values('data_id')
            ).values('pk')
        )
        return q

authorization.register(NotificationAnswer, factory=NotificationAnswerQFactory)

class ChecklistQFactory(authorization.QFactory):
    def get_q(self, user):
        if user.profile.is_internal:
            return self.make_q()

        involved_by_task = self.make_q(submission__pk__in=
            Task.objects.filter(
                content_type=ContentType.objects.get_for_model(Submission),
            ).values('data_id')
        )
        involved_as_presenting_party = (
            self.make_q(submission__current_submission_form__sponsor=user) |
            self.make_q(submission__current_submission_form__submitter=user) |
            self.make_q(submission__current_submission_form__primary_investigator__user=user) |
            self.make_q(submission__presenter=user) |
            self.make_q(submission__susar_presenter=user)
        )

        temporary_authorized = self.make_q(submission__in=
            TemporaryAuthorization.objects.active(user=user)
                .values('submission_id')
        )

        q = self.make_q(last_edited_by=user)
        q |= (involved_by_task | temporary_authorized) & ~involved_as_presenting_party & self.make_q(status__in=['completed', 'review_ok'])
        q |= involved_as_presenting_party & self.make_q(status='review_ok')
        return q

authorization.register(Checklist, factory=ChecklistQFactory)
authorization.register(ChecklistAnswer, lookup='checklist')


class MeetingQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.profile
        if profile.is_internal:
            return self.make_q()
        elif profile.is_board_member or profile.is_resident_member or \
            profile.is_omniscient_member:
            return self.make_q(ended=None)
        else:
            return self.make_deny_q()

authorization.register(Meeting, factory=MeetingQFactory)
authorization.register(TimetableEntry, lookup='meeting')
authorization.register(Participation, lookup='entry__meeting')
