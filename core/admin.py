# -*- coding: utf-8 -*-

from django.contrib import admin

from ecs.core.models import ChecklistBlueprint, ChecklistQuestion, Checklist, ChecklistAnswer
from ecs.core.models import DocumentType, Document, EthicsCommission, SubmissionForm, Investigator
from ecs.core.models import InvestigatorEmployee, Measure, NonTestedUsedDrug
from ecs.core.models import ForeignParticipatingCenter, Amendment, NotificationType, Notification
from ecs.core.models import VoteReview, Vote, SubmissionReview, Submission, NotificationAnswer, MedicalCategory
from ecs.core.models import UserProfile
#from ecs.core.models import Workflow, Checklist, Meeting
# Revision, Message, AuditLog, Reviewer, Annotation


# Nicer Checklist Editing
class ChecklistQuestionInline(admin.TabularInline):
    model = ChecklistQuestion

class ChecklistBlueprintAdmin(admin.ModelAdmin):
    inlines = [
        ChecklistQuestionInline,
    ]


class ChecklistAnswerInline(admin.TabularInline):
    model = ChecklistAnswer

class ChecklistAdmin(admin.ModelAdmin):
    inlines = [
        ChecklistAnswerInline,
    ]


admin.site.register(ChecklistBlueprint, ChecklistBlueprintAdmin)
admin.site.register(ChecklistQuestion)
admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(ChecklistAnswer)
admin.site.register(DocumentType)
admin.site.register(Document)
admin.site.register(EthicsCommission)
admin.site.register(SubmissionForm)
admin.site.register(Investigator)
admin.site.register(InvestigatorEmployee)
admin.site.register(Measure)
admin.site.register(NonTestedUsedDrug)
admin.site.register(ForeignParticipatingCenter)
admin.site.register(Amendment)
admin.site.register(NotificationType)
admin.site.register(Notification)
admin.site.register(VoteReview)
admin.site.register(Vote)
admin.site.register(SubmissionReview)
admin.site.register(Submission)
admin.site.register(NotificationAnswer)
admin.site.register(MedicalCategory)
admin.site.register(UserProfile)
