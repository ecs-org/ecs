# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.contenttypes.models import ContentType

from ecs import authorization
from ecs.core.models import (Submission, SubmissionForm, Investigator, InvestigatorEmployee,
    Measure, ForeignParticipatingCenter, NonTestedUsedDrug, ExpeditedReviewCategory)
from ecs.core.models.constants import SUBMISSION_LANE_RETROSPECTIVE_THESIS, SUBMISSION_LANE_EXPEDITED
from ecs.checklists.models import Checklist, ChecklistAnswer
from ecs.votes.models import Vote
from ecs.documents.models import Document, DocumentPersonalization, Page
from ecs.votes.constants import FINAL_VOTE_RESULTS
from ecs.docstash.models import DocStash, DocStashData
from ecs.tasks.models import Task
from ecs.notifications.models import Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification
from ecs.pdfviewer.models import DocumentAnnotation
from ecs.meetings.models import Meeting, AssignedMedicalCategory, TimetableEntry, Participation, Constraint
from ecs.audit.models import AuditTrail
from ecs.billing.models import ChecklistBillingState
from ecs.scratchpad.models import ScratchPad
from ecs.boilerplate.models import Text
from ecs.communication.models import Thread, Message

class SubmissionQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.get_profile()

        ### shortcircuit logic
        if not profile.is_approved_by_office:
            return self.make_deny_q()
            
        ### default policy: only avaiable for the (susar) presenter.
        q = self.make_q(forms__presenter=user) | self.make_q(forms__susar_presenter=user)
        
        ### explicit temporary permissions
        now = datetime.now()
        q |= self.make_q(temp_auth__user=user, temp_auth__start__lte=now, temp_auth__end__gt=now)

        ### rules that apply until a final vote has been published.
        until_vote_q = self.make_q(external_reviewers=user)
        if profile.is_thesis_reviewer:
            until_vote_q |= self.make_q(workflow_lane=SUBMISSION_LANE_RETROSPECTIVE_THESIS)
        if profile.is_board_member:
            until_vote_q |= self.make_q(timetable_entries__participations__user=user)
        if profile.is_expedited_reviewer:
            until_vote_q |= self.make_q(workflow_lane=SUBMISSION_LANE_EXPEDITED)
        if profile.is_insurance_reviewer:
            until_vote_q |= self.make_q(insurance_review_required=True)
            q |= self.make_q(forms__notifications__review_lane='insrev')
        q |= until_vote_q & (
            self.make_q(current_submission_form__current_published_vote=None)
            | ~self.make_q(current_submission_form__current_published_vote__result__in=FINAL_VOTE_RESULTS)
        )

        ### rules that apply until the end of the submission lifecycle
        until_eol_q = self.make_q(pk__gt=0)
        if not (user.is_staff or profile.is_internal):
            until_eol_q &= self.make_q(
                current_submission_form__submitter=user
            ) | self.make_q(
                current_submission_form__primary_investigator__user=user
            ) | self.make_q(
                current_submission_form__sponsor=user
            ) | self.make_q(
                pk__in=Task.objects.filter(content_type=ContentType.objects.get_for_model(Submission)).values('data_id').query
            ) | self.make_q(
                pk__in=Checklist.objects.values('submission__pk').query
            )
        q |= until_eol_q
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
        profile = user.get_profile()
        q = self.make_q(submission_form__submission__pk__in=Submission.objects.values('pk').query)
        if not profile.is_internal:
            q &= self.make_q(published_at__isnull=False)
        return q

authorization.register(Vote, factory=VoteQFactory)

class DocumentQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q() # FIXME: how should document authorization work?
        submission_q = self.make_q(content_type=ContentType.objects.get_for_model(SubmissionForm))
        q = ~submission_q | (submission_q & self.make_q(object_id__in=SubmissionForm.objects.values('pk').query))
        return q

authorization.register(Document, factory=DocumentQFactory)
authorization.register(DocumentPersonalization, lookup='document')
authorization.register(Page, lookup='doc')

class DocstashQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q(owner=user)

authorization.register(DocStash, factory=DocstashQFactory)
authorization.register(DocStashData, lookup='stash')

class TaskQFactory(authorization.QFactory):
    def get_q(self, user):
        q = self.make_q(task_type__groups__in=user.groups.all().values('pk').query) | self.make_q(created_by=user) | self.make_q(assigned_to=user)
        q &= ~(self.make_q(expedited_review_categories__gt=0) & ~self.make_q(expedited_review_categories__in=ExpeditedReviewCategory.objects.filter(users=user)))
        return q

authorization.register(Task, factory=TaskQFactory)

class NotificationQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q(submission_forms__submission__in=Submission.objects.values('pk').query)

for cls in (Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification):
    authorization.register(cls, factory=NotificationQFactory)

#authorization.register(NotificationAnswer, lookup='notification')

class ChecklistQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.get_profile()
        if profile.is_internal:
            return self.make_q()
        q = self.make_q(user=user)
        q |= self.make_q(status='review_ok', submission__pk__in=Task.objects.filter(content_type=ContentType.objects.get_for_model(Submission)).values('data_id').query)
        for x in ('sponsor', 'invoice', 'submitter', 'presenter', 'susar_presenter'):
            kwargs = {'status': 'review_ok', 'submission__current_submission_form__{0}'.format(x): user}
            q |= self.make_q(**kwargs)
        return q

authorization.register(Checklist, factory=ChecklistQFactory)
authorization.register(ChecklistAnswer, lookup='checklist')

class DocumentAnnotationQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q(user=user)

authorization.register(DocumentAnnotation, factory=DocumentAnnotationQFactory)

class MeetingQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.get_profile()
        if profile.is_internal or user.groups.filter(name='EC-Thesis Executive Group').exists():
            return self.make_q()
        else:
            return self.make_deny_q()

authorization.register(Meeting, factory=MeetingQFactory)
authorization.register(AssignedMedicalCategory, lookup='meeting')
authorization.register(TimetableEntry, lookup='meeting')
authorization.register(Participation, lookup='entry__meeting')
authorization.register(Constraint, lookup='meeting')

class AuditTrailQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.get_profile()
        if profile.is_executive_board_member:
            return self.make_q()
        else:
            return self.make_deny_q()

authorization.register(AuditTrail, factory=AuditTrailQFactory)

class ChecklistBillingStateQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.get_profile()
        if profile.is_internal:
            return self.make_q()
        else:
            return self.make_deny_q()

authorization.register(ChecklistBillingState, factory=ChecklistBillingStateQFactory)

class ScratchPadQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q(owner=user)

authorization.register(ScratchPad, factory=ScratchPadQFactory)

class TextQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.get_profile()
        if profile.is_internal:
            return self.make_q()
        else:
            return self.make_deny_q()

authorization.register(Text, factory=TextQFactory)

class ThreadQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.get_profile()
        if profile.is_internal:
            return self.make_q()

        return self.make_q(sender=user) | self.make_q(receiver=user)

authorization.register(Thread, factory=ThreadQFactory)
authorization.register(Message, lookup='thread')
