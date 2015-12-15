# -*- coding: utf-8 -*-
from django.contrib import admin

from ecs.core.models import EthicsCommission, SubmissionForm, Investigator
from ecs.core.models import InvestigatorEmployee, Measure, NonTestedUsedDrug
from ecs.core.models import ForeignParticipatingCenter
from ecs.core.models import Submission, MedicalCategory

admin.site.register(EthicsCommission)
admin.site.register(SubmissionForm)
admin.site.register(Investigator)
admin.site.register(InvestigatorEmployee)
admin.site.register(Measure)
admin.site.register(NonTestedUsedDrug)
admin.site.register(ForeignParticipatingCenter)
admin.site.register(Submission)
admin.site.register(MedicalCategory)
