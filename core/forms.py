from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory

from ecs.core.models import Document, Investigator, SubmissionForm, Measure, ForeignParticipatingCenter, NonTestedUsedDrug
from ecs.core.models import BaseNotificationForm as BaseNotification
from ecs.core.models import ExtendedNotificationForm as ExtendedNotification

## custom form fields ##

DATE_INPUT_FORMATS = ("%d.%m.%Y", "%Y-%m-%d")

class DateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', DATE_INPUT_FORMATS)
        super(DateField, self).__init__(*args, **kwargs)

class InvestigatorChoiceMixin(object):
    def __init__(self, **kwargs):
        kwargs.setdefault('queryset', Investigator.objects.order_by('name'))
        super(InvestigatorChoiceMixin, self).__init__(**kwargs)

    def label_from_instance(self, obj):
        return u"%s (%s)" % (obj.name, obj.ethics_commission.name)

class InvestigatorChoiceField(InvestigatorChoiceMixin, forms.ModelChoiceField): pass
class InvestigatorMultipleChoiceField(InvestigatorChoiceMixin, forms.ModelMultipleChoiceField): pass

## forms ##

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
        
class DocumentUploadForm(forms.ModelForm):
    date = DateField(required=True)
    
    class Meta:
        model = Document
        exclude = ('uuid_document', 'uuid_document_revision', 'mimetype', 'deleted')
        
class SubmissionFormForm(forms.ModelForm):
    submitter_sign_date = DateField(required=True)

    class Meta:
        model = SubmissionForm
        exclude = ('submission', 'documents', 'ethics_commissions')

MeasureFormSet = modelformset_factory(Measure, extra=1, exclude = ('submission_form',))

ForeignParticipatingCenterFormSet = modelformset_factory(ForeignParticipatingCenter, extra=1, exclude=('submission_form',))

NonTestedUsedDrugFormSet = modelformset_factory(NonTestedUsedDrug, extra=1, exclude=('submission_form',))