# -*- coding: utf-8 -*-
import tempfile
from cStringIO import StringIO
import os

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

from ecs.core.forms.forms import ModelFormPickleMixin
from ecs.core.forms.fields import DateField
from ecs.documents.models import Document, DocumentType
from ecs.utils.pdfutils import pdf_isvalid, pdf2pdfa
from ecs.utils.formutils import require_fields
from ecs.utils.pathutils import tempfilecopy


class DocumentForm(ModelFormPickleMixin, forms.ModelForm):
    date = DateField(required=True)
    doctype = forms.ModelChoiceField(queryset=DocumentType.objects.exclude(hidden=True), required=False)

    def clean_file(self):
        pdf = self.cleaned_data['file']
        if not pdf:
            raise ValidationError(_(u'no file'))

        # make a copy for introspection on user errors (or system errors)
        tmp_dir = os.path.join(settings.TEMPFILE_DIR, 'incoming-copy')
        tempfilecopy(pdf, tmp_dir=tmp_dir, mkdir=True, suffix='.pdf')

        if not pdf_isvalid(pdf):
            pdf.seek(0)
            raise ValidationError(_(u'This Document is not a valid PDF document.'))

        pdf.seek(0)
        # TODO: fix ghostscript (pdf2pdfa breaks some documents)
        """
        pdfa = StringIO()       # TODO: use temporary file to save memory
        size = pdf2pdfa(pdf, pdfa)
        pdf.close()
        pdfa.seek(0)
        """
        pdfa = pdf


        self.cleaned_data['file'] = pdfa        # XXX: do we need this?

        return UploadedFile(pdfa, pdf.name, pdf.content_type, size, pdf.charset)

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
