from django import forms

from ecs.core.models import Document
from ecs.core.models import BaseNotificationForm as BaseNotification
from ecs.core.models import ExtendedNotificationForm as ExtendedNotification

DATE_INPUT_FORMATS = ("%d.%m.%Y", "%Y-%m-%d")

class BaseNotificationForm(forms.ModelForm):
    date_of_vote = forms.DateField(required=False, input_formats=DATE_INPUT_FORMATS)
    signed_on = forms.DateField(required=False, input_formats=DATE_INPUT_FORMATS)

    class Meta:
        model = BaseNotification
        exclude = ('type', 'notification')
        
class ExtendedNotificationForm(forms.ModelForm):
    class Meta:
        model = ExtendedNotification
        exclude = ('type', 'notification')
        
class DocumentUploadForm(forms.ModelForm):
    date = forms.DateField(required=True, input_formats=DATE_INPUT_FORMATS)
    
    class Meta:
        model = Document
        exclude = ('uuid_document', 'uuid_document_revision', 'mimetype', 'absent')