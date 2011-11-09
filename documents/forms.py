# -*- coding: utf-8 -*-
from cStringIO import StringIO
import os
import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

from ecs.utils.formutils import ModelFormPickleMixin
from ecs.core.forms.fields import DateField
from ecs.documents.models import Document, DocumentType
from ecs.utils.pdfutils import sanitize_pdf, PDFValidationError
from ecs.utils.formutils import require_fields
from ecs.utils.pathutils import tempfilecopy

PDF_MAGIC = '%PDF'

logger = logging.getLogger(__name__)

class DocumentForm(ModelFormPickleMixin, forms.ModelForm):
    date = DateField(required=True)
    doctype = forms.ModelChoiceField(queryset=DocumentType.objects.exclude(is_hidden=True), required=False)

    def clean_file(self):
        pdf = self.cleaned_data['file']
        if not pdf:
            raise ValidationError(_(u'no file'))

        # make a copy for introspection on user errors (or system errors)
        tmp_dir = os.path.join(settings.TEMPFILE_DIR, 'incoming-copy')
        tempfilecopy(pdf, tmp_dir=tmp_dir, mkdir=True, suffix='.pdf')
        pdf.seek(0)
        
        self.pdf_error = False

        # pdf magic check
        if pdf.read(4) != PDF_MAGIC:
            raise ValidationError(_(u'This file is not a PDF document.'))
        pdf.seek(0)
        
        # sanitization
        try:
            f = sanitize_pdf(pdf)
        except PDFValidationError as e:
            logger.error('unreadable pdf document: %s' % e)
            self.pdf_error = True
            raise ValidationError(_(u'Your PDF document could not be processed.'))

        while f.read(1024):
            pass
        size = f.tell()
        f.seek(0)

        return UploadedFile(f, pdf.name, 'application/pdf', size, pdf.charset)

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
        return obj

    class Meta:
        model = Document
        fields = ('file', 'name', 'doctype', 'version', 'date', 'replaces_document')
        widgets = {'replaces_document': forms.HiddenInput()}
