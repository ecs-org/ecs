# -*- coding: utf-8 -*
from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory

from ecs.core.models import Document, Investigator, InvestigatorEmployee, SubmissionForm, Measure, ForeignParticipatingCenter, NonTestedUsedDrug
from ecs.core.models import Notification, CompletionReportNotification, ProgressReportNotification

from ecs.core.forms.fields import DateField, NullBooleanField, InvestigatorChoiceField, InvestigatorMultipleChoiceField

## notifications ##

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')
        

class ProgressReportNotificationForm(NotificationForm):
    runs_till = DateField()

    class Meta:
        model = ProgressReportNotification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')

class CompletionReportNotificationForm(NotificationForm):
    completion_date = DateField()

    class Meta:
        model = CompletionReportNotification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')

## submissions ##

class SubmissionFormForm(forms.ModelForm):
    substance_preexisting_clinical_tries = NullBooleanField(required=False)
    substance_p_c_t_gcp_rules = NullBooleanField(required=False)
    substance_p_c_t_final_report = NullBooleanField(required=False)

    medtech_certified_for_exact_indications = NullBooleanField(required=False)
    medtech_certified_for_other_indications = NullBooleanField(required=False)
    medtech_ce_symbol = NullBooleanField(required=False)
    medtech_manual_included = NullBooleanField(required=False)
    
    # non model fields (required for validation)
    invoice_differs_from_sponsor = forms.BooleanField(required=False, label=u'Der Rechnungsempfänger ist nicht der Sponsor')

    class Meta:
        model = SubmissionForm
        exclude = ('submission', 'documents', 'ethics_commissions', 'date_of_receipt')
        
    def clean(self):
        cleaned_data = super(SubmissionFormForm, self).clean()
        return cleaned_data

## documents ##
        
class DocumentForm(forms.ModelForm):
    date = DateField(required=True)
    
    def clean(self):
        file = self.cleaned_data.get('file')
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


class BaseInvestigatorFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Investigator.objects.none())
        super(BaseInvestigatorFormSet, self).__init__(*args, **kwargs)

InvestigatorFormSet = modelformset_factory(Investigator, formset=BaseInvestigatorFormSet, extra=1, 
                                           fields = ('organisation', 'ethics_commission', 'main', 'name', 'phone', 'mobile', 'fax', 'email', 'jus_practicandi', 'specialist', 'certified', 'subject_count',)) 


class BaseInvestigatorEmployeeFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', InvestigatorEmployee.objects.none())
        super(BaseInvestigatorEmployeeFormSet, self).__init__(*args, **kwargs)
    def add_fields(self, form, index):
        super(BaseInvestigatorEmployeeFormSet, self).add_fields(form, index)
        form.fields['investigator_index'] = forms.IntegerField(required=True,widget=forms.HiddenInput(attrs={'value' : 0}))

InvestigatorEmployeeFormSet = modelformset_factory(InvestigatorEmployee, formset=BaseInvestigatorEmployeeFormSet, extra=1, exclude = ('submission',))

