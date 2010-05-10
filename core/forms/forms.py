# -*- coding: utf-8 -*
from django import forms
from django.contrib.auth.models import User
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory
from django.utils.safestring import mark_safe

from ecs.core.models import Document, Investigator, InvestigatorEmployee, SubmissionForm, Measure, ForeignParticipatingCenter, NonTestedUsedDrug, Submission
from ecs.core.models import Notification, CompletionReportNotification, ProgressReportNotification
from ecs.core.models import MedicalCategory

from ecs.core.forms.fields import DateField, NullBooleanField, InvestigatorChoiceField, InvestigatorMultipleChoiceField
from ecs.core.forms.utils import ReadonlyFormMixin, ReadonlyFormSetMixin


def _unpickle(f, args, kwargs):
    return globals()[f.replace('FormFormSet', 'FormSet')](*args, **kwargs)
    
class ModelFormPickleMixin(object):
    def __reduce__(self):
        return (_unpickle, (self.__class__.__name__, (), {'data': self.data or None, 'prefix': self.prefix, 'initial': self.initial}))
        
class ModelFormSetPickleMixin(object):
    def __reduce__(self):
        return (_unpickle, (self.__class__.__name__, (), {'data': self.data or None, 'prefix': self.prefix, 'initial': self.initial}))

## notifications ##

class NotificationForm(ModelFormPickleMixin, forms.ModelForm):
    class Meta:
        model = Notification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')
        

class ProgressReportNotificationForm(NotificationForm):
    runs_till = DateField(required=True)

    class Meta:
        model = ProgressReportNotification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')

class CompletionReportNotificationForm(ModelFormPickleMixin):
    completion_date = DateField(required=True)

    class Meta:
        model = CompletionReportNotification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')

## submissions ##

class SubmissionEditorForm(forms.ModelForm):
    class Meta:
        model = Submission

class SubmissionFormForm(ReadonlyFormMixin, ModelFormPickleMixin, forms.ModelForm):

    substance_preexisting_clinical_tries = NullBooleanField(required=False)
    substance_p_c_t_gcp_rules = NullBooleanField(required=False)
    substance_p_c_t_final_report = NullBooleanField(required=False)

    medtech_certified_for_exact_indications = NullBooleanField(required=False)
    medtech_certified_for_other_indications = NullBooleanField(required=False)
    medtech_ce_symbol = NullBooleanField(required=False)
    medtech_manual_included = NullBooleanField(required=False)
    
    # non model fields (required for validation)
    invoice_differs_from_sponsor = forms.BooleanField(required=False, label=u'Der Rechnungsempfänger ist nicht der Sponsor')
    # FIXME: the following fields do not belong here
    #medical_categories = forms.ModelMultipleChoiceField(MedicalCategory.objects.all(), label=u'Medizinische Kategorien')
    #thesis = forms.NullBooleanField(required=False)
    #retrospective = forms.NullBooleanField(required=False)
    #expedited = forms.NullBooleanField(required=False)
    #external_reviewer = forms.NullBooleanField(required=False)
    #external_reviewer_name = forms.ModelChoiceField(User.objects.all(), required=False)

    class Meta:
        model = SubmissionForm
        exclude = ('submission', 'documents', 'ethics_commissions', 'date_of_receipt')
        
    def clean(self):
        cleaned_data = super(SubmissionFormForm, self).clean()
        return cleaned_data

## documents ##
        
class DocumentForm(ModelFormPickleMixin, forms.ModelForm):
    date = DateField(required=True)
    
    def clean(self):
        file = self.cleaned_data.get('file')
        if not self.cleaned_data.get('original_file_name') and file:
            self.cleaned_data['original_file_name'] = file.name
        return self.cleaned_data
        
    def save(self, commit=True):
        obj = super(DocumentForm, self).save(commit=False)
        obj.original_file_name = self.cleaned_data.get('original_file_name')
        if commit:
            obj.save()
        return obj
    
    class Meta:
        model = Document
        exclude = ('uuid_document', 'uuid_document_revision', 'mimetype', 'deleted', 'original_file_name')

class BaseDocumentFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Document.objects.none())
        super(BaseDocumentFormSet, self).__init__(*args, **kwargs)
        
DocumentFormSet = modelformset_factory(Document, formset=BaseDocumentFormSet, extra=1, form=DocumentForm)

## ##

class BaseForeignParticipatingCenterFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', ForeignParticipatingCenter.objects.none())
        super(BaseForeignParticipatingCenterFormSet, self).__init__(*args, **kwargs)

ForeignParticipatingCenterFormSet = modelformset_factory(ForeignParticipatingCenter, formset=BaseForeignParticipatingCenterFormSet, extra=1, exclude=('submission_form',))

class BaseNonTestedUsedDrugFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', NonTestedUsedDrug.objects.none())
        super(BaseNonTestedUsedDrugFormSet, self).__init__(*args, **kwargs)
        
NonTestedUsedDrugFormSet = modelformset_factory(NonTestedUsedDrug, formset=BaseNonTestedUsedDrugFormSet, extra=1, exclude=('submission_form',))

class MeasureForm(ModelFormPickleMixin, forms.ModelForm):
    category = forms.CharField(widget=forms.HiddenInput(attrs={'value': '6.1'}))
    
    class Meta:
        model = Measure
        exclude = ('submission_form',)
        
class RoutineMeasureForm(MeasureForm):
    category = forms.CharField(widget=forms.HiddenInput(attrs={'value': '6.2'}))

class BaseMeasureFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Measure.objects.none())
        super(BaseMeasureFormSet, self).__init__(*args, **kwargs)
        
MeasureFormSet = modelformset_factory(Measure, formset=BaseMeasureFormSet, extra=1, form=MeasureForm)
RoutineMeasureFormSet = modelformset_factory(Measure, formset=BaseMeasureFormSet, extra=1, form=RoutineMeasureForm)


class BaseInvestigatorFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Investigator.objects.none())
        super(BaseInvestigatorFormSet, self).__init__(*args, **kwargs)

InvestigatorFormSet = modelformset_factory(Investigator, formset=BaseInvestigatorFormSet, extra=1, 
                                           fields = ('organisation', 'subject_count', 'ethics_commission', 'main', 'name', 'phone', 'mobile', 'fax', 'email', 'jus_practicandi', 'specialist', 'certified',)) 

class BaseInvestigatorEmployeeFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', InvestigatorEmployee.objects.none())
        super(BaseInvestigatorEmployeeFormSet, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super(BaseInvestigatorEmployeeFormSet, self).add_fields(form, index)
        form.fields['investigator_index'] = forms.IntegerField(required=True, initial=0, widget=forms.HiddenInput())

InvestigatorEmployeeFormSet = modelformset_factory(InvestigatorEmployee, formset=BaseInvestigatorEmployeeFormSet, extra=1, exclude = ('submission',))

