# -*- coding: utf-8 -*-
from django.contrib import admin

from ecs.checklists.models import ChecklistBlueprint, ChecklistQuestion, Checklist, ChecklistAnswer


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
