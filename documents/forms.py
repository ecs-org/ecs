# -*- coding: utf-8 -*-
from tempfile import TemporaryFile
from shutil import copyfileobj

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import UploadedFile

from ecs.utils.formutils import ModelFormPickleMixin
from ecs.core.forms.fields import DateField
from ecs.documents.models import Document, DocumentType
from ecs.utils.pdfutils import decrypt_pdf
from ecs.utils.formutils import require_fields

PDF_MAGIC = '%PDF'

class DocumentForm(ModelFormPickleMixin, forms.ModelForm):
    file = forms.FileField(required=True)
    doctype = forms.ModelChoiceField(queryset=DocumentType.objects.exclude(is_hidden=True), required=False)
    date = DateField(required=True)

    def clean_file(self):
        pdf = self.cleaned_data['file']
        if not pdf:
            raise ValidationError(_(u'no file'))

        # pdf magic check
        if pdf.read(4) != PDF_MAGIC:
            raise ValidationError(_(u'This file is not a PDF document.'))
        pdf.seek(0)

        # XXX: Depending on the upload handler, pdf might not be backed by a
        # real file. If not, we must create one for usage by decrypt_pdf().
        if not hasattr(pdf, 'fileno'):
            f = TemporaryFile()
            copyfileobj(pdf, f)
            f.seek(0)
            pdf.close()
            pdf = f
        
        # sanitization
        try:
            f = decrypt_pdf(pdf)
        except ValueError:
            raise ValidationError(_('The PDF-File seems to broken. For more Information click on the question mark in the sidebar.'))

        f.seek(0)
        return UploadedFile(f, content_type='application/pdf')

    def clean(self):
        cd = super(DocumentForm, self).clean()
        replaced_document = cd.get('replaces_document', None)

        if not replaced_document:
            require_fields(self, ('doctype',))
            self.fields['doctype'].required = True
            if 'doctype' in cd.keys() and not cd['doctype']:
                del cd['doctype']
        else:
            cd['doctype'] = getattr(replaced_document, 'doctype')

        return cd

    def save(self, commit=True):
        obj = super(DocumentForm, self).save(commit=False)
        obj.original_file_name = self.cleaned_data.get('original_file_name')
        if commit:
            obj.save()
            obj.store(self.cleaned_data.get('file'))
        return obj

    class Meta:
        model = Document
        fields = ('name', 'doctype', 'version', 'date', 'replaces_document')
        widgets = {'replaces_document': forms.HiddenInput()}
