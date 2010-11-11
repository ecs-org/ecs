# -*- coding: utf-8 -*-

from datetime import datetime

from django import forms
from django.utils.translation import ugettext as _
from django.forms.models import modelformset_factory

from ecs.fastlane.models import FastLaneMeeting, AssignedFastLaneCategory
from ecs.core.forms.fields import DateTimeField

class FastLaneMeetingForm(forms.ModelForm):
    start = DateTimeField(label=_(u'Datum und Uhrzeit'), initial=datetime.now)
    class Meta:
        model = FastLaneMeeting
        fields = ('start', 'title')

class AssignedFastLaneCategoryForm(forms.ModelForm):
    class Meta:
        model = AssignedFastLaneCategory
        fields = ('user',)

