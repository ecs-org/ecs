# -*- coding: utf-8 -*-
import tempfile
from cStringIO import StringIO

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import UploadedFile

from ecs.core.forms.forms import ModelFormPickleMixin
from ecs.core.forms.fields import DateField
from ecs.documents.models import Document
from ecs.utils.pdfutils import pdf_isvalid, pdf2pdfa


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
        pdf = self.cleaned_data['file']
        if not pdf:
            return

        if not pdf_isvalid(pdf):
            pdf.seek(0)
            raise ValidationError(_(u'This Document is not a valid PDF document.'))

        pdf.seek(0)
        pdfa = StringIO()
        size = pdf2pdfa(pdf, pdfa)
        pdf.close()
        pdfa.seek(0)
        self.cleaned_data['file'] = pdfa

        return UploadedFile(pdfa, pdf.name, pdf.content_type, size, pdf.charset)

    def clean(self):
        cd = self.cleaned_data
        replaced_document = cd.get('replaces_document', None)
        if replaced_document:
            for f in ('doctype', 'name'):
                cd[f] = getattr(replaced_document, f)
                if f in self._errors.keys():
                    del self._errors[f]

        return cd

    class Meta:
        model = Document
        fields = ('file', 'doctype', 'name', 'version', 'date', 'replaces_document')
        widgets = {
            'replaces_document': forms.HiddenInput(),
        }


