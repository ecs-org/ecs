# -*- coding: utf-8 -*-

from datetime import datetime

from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy
from django.forms.models import modelformset_factory
from django.contrib.auth.models import User

from ecs.fastlane.models import FastLaneMeeting, AssignedFastLaneCategory, FastLaneTop
from ecs.core.forms.fields import DateTimeField

class FastLaneMeetingForm(forms.ModelForm):
    start = DateTimeField(label=ugettext_lazy(u'date and time'), initial=datetime.now)
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

class FastLaneTopForm(forms.ModelForm):
    class Meta:
        model = FastLaneTop
        fields = ('recommendation', 'recommendation_comment', )

