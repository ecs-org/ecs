# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ecs.core.forms.forms import ModelFormPickleMixin
from ecs.core.forms.fields import DateField
from ecs.documents.models import Document
from ecs.utils.pdfutils import pdf_isvalid


class SimpleDocumentForm(ModelFormPickleMixin, forms.ModelForm):
    date = DateField(required=True)

    def clean(self):
        file = self.cleaned_data.get('file')
        if not self.cleaned_data.get('original_file_name') and file:
            self.cleaned_data['original_file_name'] = file.name
        return self.cleaned_data
        
    def save(self, commit=True):
        obj = super(SimpleDocumentForm, self).save(commit=False)
        obj.original_file_name = self.cleaned_data.get('original_file_name')
        if commit:
            obj.save()
        return obj
    
    class Meta:
        model = Document
        fields = ('file', 'date', 'version')


class DocumentForm(SimpleDocumentForm):
    def clean_file(self):
        file = self.cleaned_data['file']
        if not file:
            return

        if not pdf_isvalid(file):
            file.seek(0)
            raise ValidationError(_(u'This Document is not a valid PDF document.'))

        file.seek(0)
        return file
        
    class Meta:
        model = Document
        fields = ('file', 'doctype', 'name', 'version', 'date', 'replaces_document')
        widgets = {
            'replaces_document': forms.HiddenInput(),
        }


