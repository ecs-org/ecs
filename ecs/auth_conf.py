from django.contrib.contenttypes.models import ContentType

from ecs import authorization
from ecs.core.models import (Submission, SubmissionForm, Investigator, InvestigatorEmployee,
    Measure, ForeignParticipatingCenter, NonTestedUsedDrug, ExpeditedReviewCategory,
    TemporaryAuthorization, MySubmission)
from ecs.checklists.models import Checklist, ChecklistAnswer
from ecs.votes.models import Vote
from ecs.documents.models import Document
from ecs.docstash.models import DocStash, DocStashData
from ecs.tasks.models import Task
from ecs.notifications.models import Notification, AmendmentNotification, SafetyNotification, NotificationAnswer, NOTIFICATION_MODELS
from ecs.meetings.models import Meeting, AssignedMedicalCategory, TimetableEntry, Participation, Constraint
from ecs.votes.constants import PERMANENT_VOTE_RESULTS


class SubmissionQFactory(authorization.QFactory):
    def get_q(self, user):
        ### internal users can see all submissions
        if user.is_staff or user.profile.is_internal:
            return self.make_q()

        q = self.make_q(id__in=
            MySubmission.objects.filter(user_id=user.id).values('submission_id'))
        
        ### explicit temporary permissions
        q |= self.make_q(id__in=TemporaryAuthorization.objects.active(user=user).values('submission_id').query)

        ### permissions until final vote is published
        until_vote_q = self.make_q(pk__in=Checklist.objects.values('submission__pk').query)
        until_vote_q |= self.make_q(pk__in=Task.objects.filter(content_type=ContentType.objects.get_for_model(Submission)).values('data_id').query)
        if user.profile.is_insurance_reviewer:
            until_vote_q |= self.make_q(forms__votes__insurance_review_required=True)
        q |= until_vote_q & ~self.make_q(forms__current_published_vote__result__in=PERMANENT_VOTE_RESULTS)

        notification_cts = map(ContentType.objects.get_for_model,
            (AmendmentNotification, SafetyNotification))
        q |= self.make_q(forms__notifications__pk__in=
            Task.objects.filter(content_type__in=notification_cts).open()
                .values('data_id'))

        return q

authorization.register(Submission, factory=SubmissionQFactory)
authorization.register(SubmissionForm, lookup='submission')
authorization.register(Investigator, lookup='submission_form__submission')
authorization.register(InvestigatorEmployee, lookup='investigator__submission_form__submission')
authorization.register(Measure, lookup='submission_form__submission')
authorization.register(NonTestedUsedDrug, lookup='submission_form__submission')
authorization.register(ForeignParticipatingCenter, lookup='submission_form__submission')

class VoteQFactory(authorization.QFactory):
    def get_q(self, user):
        q = self.make_q(submission_form__submission__pk__in=Submission.objects.values('pk').query)
        if not user.profile.is_internal:
            q &= self.make_q(published_at__isnull=False)
        if user.profile.is_insurance_reviewer:
            q |= self.make_q(insurance_review_required=True)
        return q

authorization.register(Vote, factory=VoteQFactory)

class DocumentQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q() # FIXME: how should document authorization work?
        submission_q = self.make_q(content_type=ContentType.objects.get_for_model(SubmissionForm))
        q = ~submission_q | (submission_q & self.make_q(object_id__in=SubmissionForm.objects.values('pk').query))
        return q

authorization.register(Document, factory=DocumentQFactory)

class DocstashQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q(owner=user)

authorization.register(DocStash, factory=DocstashQFactory)
authorization.register(DocStashData, lookup='stash')

class TaskQFactory(authorization.QFactory):
    def get_q(self, user):
        q = self.make_q(task_type__groups__in=user.groups.values('pk').query) & (self.make_q(assigned_to=None) | self.make_q(assigned_to__profile__is_indisposed=True))
        q |= self.make_q(created_by=user) | self.make_q(assigned_to=user)
        q &= ~self.make_q(expedited_review_categories__gt=0) | self.make_q(expedited_review_categories__in=ExpeditedReviewCategory.objects.filter(users=user).values('pk').query)
        return q

authorization.register(Task, factory=TaskQFactory)

class NotificationQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q(submission_forms__submission__in=Submission.objects.values('pk').query)

for cls in NOTIFICATION_MODELS:
    authorization.register(cls, factory=NotificationQFactory)

class NotificationAnswerQFactory(authorization.QFactory):
    def get_q(self, user):
        q = self.make_q(notification__in=Notification.objects.values('pk').query)
        if not user.profile.is_internal:
            q &= self.make_q(published_at__isnull=False)
        for cls in NOTIFICATION_MODELS:
            ct = ContentType.objects.get_for_model(cls)
            q |= self.make_q(notification__pk__in=Notification.objects.filter(pk__in=Task.objects.filter(content_type=ct).values('data_id').query).values('pk').query)
        return q

authorization.register(NotificationAnswer, factory=NotificationAnswerQFactory)

class ChecklistQFactory(authorization.QFactory):
    def get_q(self, user):
        if user.profile.is_internal:
            return self.make_q()

        involved_by_task = self.make_q(submission__pk__in=Task.objects.filter(content_type=ContentType.objects.get_for_model(Submission)).values('data_id').query)
        involved_as_presenting_party = (
            self.make_q(submission__current_submission_form__sponsor=user) |
            self.make_q(submission__current_submission_form__submitter=user) |
            self.make_q(submission__current_submission_form__primary_investigator__user=user) |
            self.make_q(submission__presenter=user) |
            self.make_q(submission__susar_presenter=user)
        )

        temporary_authorized = self.make_q(submission__in=TemporaryAuthorization.objects.active(user=user).values('submission_id').query)

        q = self.make_q(last_edited_by=user)
        q |= (involved_by_task | temporary_authorized) & ~involved_as_presenting_party & self.make_q(status__in=['completed', 'review_ok'])
        q |= involved_as_presenting_party & self.make_q(status='review_ok')
        return q

authorization.register(Checklist, factory=ChecklistQFactory)
authorization.register(ChecklistAnswer, lookup='checklist')

class MeetingQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.profile
        if profile.is_internal or profile.is_resident_member or profile.is_board_member:
            return self.make_q()
        else:
            return self.make_deny_q()

authorization.register(Meeting, factory=MeetingQFactory)
authorization.register(AssignedMedicalCategory, lookup='meeting')
authorization.register(TimetableEntry, lookup='meeting')
authorization.register(Participation, lookup='entry__meeting')
authorization.register(Constraint, lookup='meeting')
