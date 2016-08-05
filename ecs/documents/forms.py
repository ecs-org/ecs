from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import UploadedFile

from ecs.core.forms.fields import DateField
from ecs.documents.models import Document, DocumentType
from ecs.utils.pdfutils import decrypt_pdf


PDF_MAGIC = b'%PDF'

class DocumentForm(forms.ModelForm):
    file = forms.FileField(required=True)
    doctype = forms.ModelChoiceField(
        queryset=DocumentType.objects.exclude(is_hidden=True).order_by('identifier'))
    date = DateField(required=True)

    def clean_file(self):
        pdf = self.cleaned_data['file']
        if not pdf:
            raise ValidationError(_('no file'))

        # pdf magic check
        if pdf.read(4) != PDF_MAGIC:
            raise ValidationError(_('This file is not a PDF document.'))
        pdf.seek(0)
        
        # sanitization
        try:
            f = decrypt_pdf(pdf)
        except ValueError:
            raise ValidationError(_('The PDF-File seems to broken. For more Information click on the question mark in the sidebar.'))

        f.seek(0)
        return UploadedFile(f, content_type='application/pdf', name='upload.pdf')

    def clean(self):
        cd = super().clean()
        replaced_document = cd.get('replaces_document')
        if replaced_document:
            cd['doctype'] = replaced_document.doctype
        return cd

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.original_file_name = self.cleaned_data.get('original_file_name')
        if commit:
            obj.save()
            obj.store(self.cleaned_data.get('file'))
        return obj

    class Meta:
        model = Document
        fields = ('file', 'name', 'doctype', 'version', 'date', 'replaces_document')
        widgets = {'replaces_document': forms.HiddenInput()}
