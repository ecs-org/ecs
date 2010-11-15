from django import forms
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext
from ecs.core.models import Submission
from ecs.core.forms.utils import ReadonlyFormMixin
from ecs.core.forms.fields import MultiselectWidget

class CategorizationReviewForm(ReadonlyFormMixin, forms.ModelForm):
    external_reviewer_name = forms.ModelChoiceField(queryset=User.objects.filter(ecs_profile__external_review=True), required=False)
    
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective', 'medical_categories', 'expedited', 'expedited_review_categories', 'external_reviewer', 'external_reviewer_name', 
            'is_amg', 'is_mpg', 'sponsor_required_for_next_meeting', 'insurance_review_required', 'remission', 'keywords', 'additional_reviewers')
        widgets = {
            'medical_categories': MultiselectWidget(url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'medical_categories'})),
            'expedited_review_categories': MultiselectWidget(url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'expedited_review_categories'})),
            'additional_reviewers': MultiselectWidget(url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'users'})),
        }
        
    def clean(self):
        cd = self.cleaned_data
        thesis = cd.get('thesis', None)
        expedited = cd.get('expedited', None)
        print thesis, expedited
        if thesis and expedited:
            raise forms.ValidationError(ugettext("Studies cannot be classified 'expedited' and 'thesis' at the same time."))
        if thesis:
            cd['expedited'] = False
        if expedited:
            cd['thesis'] = False
        if thesis or expedited:
            cd['external_reviewer'] = False
            cd['external_reviewer_name'] = None
        return cd


class RetrospectiveThesisReviewForm(ReadonlyFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('thesis', 'retrospective',)


class BefangeneReviewForm(ReadonlyFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('befangene',)


