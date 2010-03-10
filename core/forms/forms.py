from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory

from ecs.core.models import Document, Investigator, SubmissionForm, Measure, ForeignParticipatingCenter, NonTestedUsedDrug
from ecs.core.models import BaseNotificationForm as BaseNotification
from ecs.core.models import ExtendedNotificationForm as ExtendedNotification

from ecs.core.forms.fields import DateField, NullBooleanField, InvestigatorChoiceField, InvestigatorMultipleChoiceField

## notifications ##

class BaseNotificationForm(forms.ModelForm):
    investigators = InvestigatorMultipleChoiceField()
    investigator = InvestigatorChoiceField(required=False)
    signed_on = DateField(required=False)
    
    class Meta:
        model = BaseNotification
        exclude = ('type', 'documents')
        

class ExtendedNotificationForm(BaseNotificationForm):
    aborted_on = DateField(required=False)
    runs_till = DateField(required=False)
    finished_on = DateField(required=False)
    
    class Meta:
        model = ExtendedNotification
        exclude = ('type', 'documents')
        
## submissions ##

class SubmissionFormForm(forms.ModelForm):
    substance_preexisting_clinical_tries = NullBooleanField(required=False)
    substance_p_c_t_gcp_rules = NullBooleanField(required=False)
    substance_p_c_t_final_report = NullBooleanField(required=False)

    medtech_certified_for_exact_indications = NullBooleanField(required=False)
    medtech_certified_for_other_indications = NullBooleanField(required=False)
    medtech_ce_symbol = NullBooleanField(required=False)
    medtech_manual_included = NullBooleanField(required=False)

    class Meta:
        model = SubmissionForm
        exclude = ('submission', 'documents', 'ethics_commissions')

## documents ##
        
class DocumentForm(forms.ModelForm):
    date = DateField(required=True)
    
    def clean(self):
        file = self.cleaned_data['file']
        if not self.cleaned_data.get('original_file_name') and file:
            self.cleaned_data['original_file_name'] = file.name
        return self.cleaned_data
    
    class Meta:
        model = Document
        exclude = ('uuid_document', 'uuid_document_revision', 'mimetype', 'deleted')

class BaseDocumentFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Document.objects.none())
        super(BaseDocumentFormSet, self).__init__(*args, **kwargs)
        
DocumentFormSet = modelformset_factory(Document, formset=BaseDocumentFormSet, extra=1, form=DocumentForm)

## ##

class BaseForeignParticipatingCenterFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', ForeignParticipatingCenter.objects.none())
        super(BaseForeignParticipatingCenterFormSet, self).__init__(*args, **kwargs)

ForeignParticipatingCenterFormSet = modelformset_factory(ForeignParticipatingCenter, formset=BaseForeignParticipatingCenterFormSet, extra=1, exclude=('submission_form',))

class BaseNonTestedUsedDrugFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', NonTestedUsedDrug.objects.none())
        super(BaseNonTestedUsedDrugFormSet, self).__init__(*args, **kwargs)

NonTestedUsedDrugFormSet = modelformset_factory(NonTestedUsedDrug, formset=BaseNonTestedUsedDrugFormSet, extra=1, exclude=('submission_form',))

class BaseMeasureFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Measure.objects.none())
        super(BaseMeasureFormSet, self).__init__(*args, **kwargs)

MeasureFormSet = modelformset_factory(Measure, formset=BaseMeasureFormSet, extra=1, exclude = ('submission_form',))

