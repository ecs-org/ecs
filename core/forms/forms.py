from django import forms
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory

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
        

class SubmissionFormForm(forms.ModelForm):
    submitter_sign_date = DateField(required=True)

    class Meta:
        model = SubmissionForm
        exclude = ('submission', 'documents', 'ethics_commissions')

## documents ##
        
class DocumentForm(forms.ModelForm):
    date = DateField(required=True)

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

