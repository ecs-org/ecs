# -*- coding: utf-8 -*-

from datetime import datetime

from django import forms
from django.utils.translation import ugettext as _
from django.forms.models import modelformset_factory
from django.contrib.auth.models import User

from ecs.fastlane.models import FastLaneMeeting, AssignedFastLaneCategory
from ecs.core.forms.fields import DateTimeField

class FastLaneMeetingForm(forms.ModelForm):
    start = DateTimeField(label=_(u'Datum und Uhrzeit'), initial=datetime.now)
    class Meta:
        model = FastLaneMeeting
        fields = ('start', 'title')

class AssignedFastLaneCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        rval = super(AssignedFastLaneCategoryForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['user'].queryset = User.objects.filter(expedited_review_categories=self.instance.category)
        return rval


    class Meta:
        model = AssignedFastLaneCategory
        fields = ('user',)

